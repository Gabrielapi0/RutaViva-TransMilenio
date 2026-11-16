/* RutaViva · interfaz. Toda la lógica de la red vive en el motor (Python);
   aquí solo se piden datos a la API y se dibujan. */
"use strict";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = (t) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toUpperCase();

async function api(ruta, params = {}) {
  const url = ruta + "?" + new URLSearchParams(params);
  const r = await fetch(url);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || "Error");
  return j;
}
async function post(ruta, cuerpo = {}) {
  const r = await fetch(ruta, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo) });
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || "Error");
  return j;
}
let tAviso;
function aviso(msg, error = false) {
  const a = $("#aviso");
  a.textContent = msg;
  a.classList.toggle("error", error);
  a.classList.add("ver");
  clearTimeout(tAviso);
  tAviso = setTimeout(() => a.classList.remove("ver"), 2600);
}
const ahora = () => { const d = new Date(); return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`; };

/* ------------------------------------------------ colores por troncal */
const TRONCAL = {
  A: "#0d4da1", B: "#6cb33f", C: "#e8b500", D: "#7b3f98", E: "#d6589b", F: "#e4002b", G: "#00a3e0",
  H: "#f28c28", J: "#b8935a", K: "#8b5a2b", L: "#00a99d", M: "#e5007e",
};
const colorRuta = (r) => TRONCAL[(r || " ")[0]] || "#4a5560";
const oscuraTexto = (r) => ["C"].includes((r || " ")[0]);
const insignia = (r, peq = false) =>
  `<span class="insignia${peq ? " insignia--peq" : ""}${oscuraTexto(r) ? " insignia--oscura" : ""}" style="--c:${colorRuta(r)}">${esc(r)}</span>`;
const svgBus = (cls = "") => `<svg class="${cls}" viewBox="0 0 360 92"><use href="#bus-articulado"/></svg>`;

/* ------------------------------------------------ autocompletado (R2) */
function autocompletar(input) {
  const env = document.createElement("div");
  env.className = "envoltura-ac";
  input.parentNode.insertBefore(env, input);
  env.appendChild(input);
  const lista = document.createElement("ul");
  lista.className = "lista-ac";
  lista.hidden = true;
  env.appendChild(lista);
  let sel = -1, items = [], pedido = 0;

  const cerrar = () => { lista.hidden = true; sel = -1; };
  const elegir = (v) => { input.value = v; cerrar(); input.dispatchEvent(new CustomEvent("elegido", { detail: v })); };
  const pintar = () => {
    lista.innerHTML = items.map((n, i) => {
      const p = norm(input.value).length;
      return `<li class="${i === sel ? "sel" : ""}" data-v="${esc(n)}"><svg><use href="#pic-bus"/></svg><span><mark>${esc(n.slice(0, p))}</mark>${esc(n.slice(p))}</span></li>`;
    }).join("");
    lista.hidden = items.length === 0;
  };
  input.addEventListener("input", async () => {
    const v = norm(input.value);
    if (!v) return cerrar();
    const mio = ++pedido;
    const r = await api("/api/autocompletar", { prefijo: v, k: 8 });
    if (mio !== pedido) return;
    items = r; sel = -1; pintar();
  });
  input.addEventListener("keydown", (e) => {
    if (lista.hidden) return;
    if (e.key === "ArrowDown") { sel = (sel + 1) % items.length; pintar(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { sel = (sel - 1 + items.length) % items.length; pintar(); e.preventDefault(); }
    else if (e.key === "Enter" && sel >= 0) { elegir(items[sel]); e.preventDefault(); }
    else if (e.key === "Escape") cerrar();
  });
  input.addEventListener("blur", () => setTimeout(cerrar, 150));
  lista.addEventListener("mousedown", (e) => { const li = e.target.closest("li"); if (li) elegir(li.dataset.v); });
}

/* ------------------------------------------------ pestañas */
const cargadores = {};
function mostrar(tab) {
  if (!$("#v-" + tab)) tab = "planear";
  $$(".vista").forEach((v) => (v.hidden = v.id !== "v-" + tab));
  $$("#pestanas a").forEach((a) => a.classList.toggle("activa", a.dataset.tab === tab));
  if (cargadores[tab]) cargadores[tab]();
  window.scrollTo({ top: 0 });
}
window.addEventListener("hashchange", () => mostrar(location.hash.slice(1)));

/* ------------------------------------------------ tira de ruta (señalización) */
function tira(estaciones, ruta, { editable = false, bus = false } = {}) {
  const n = estaciones.length;
  const paradas = estaciones.map((e, i) => `
    <div class="parada ${i === 0 || i === n - 1 ? "parada--extremo" : ""} ${e.estado === "cerrada" ? "parada--cerrada" : ""}">
      ${editable ? `<button class="parada__quitar" ${CAP.r7 ? "" : "hidden"} data-quitar="${esc(e.nombre)}" title="Quitar ${esc(e.nombre)}">×</button>` : ""}
      <span class="parada__punto"></span><span class="parada__nombre">${esc(e.nombre)}</span>
    </div>`).join("");
  return `<div class="tira" style="--c:${colorRuta(ruta)}">${paradas}${bus && n > 1 ? svgBus("bus-en-tira") : ""}</div>`;
}

/* ================================================ PLANEAR (R5 + R4) */
function vacioViaje() {
  $("#resultado-viaje").innerHTML = `<div class="vacio-viaje"><svg viewBox="0 0 360 92"><use href="#bus-articulado"/></svg>
    <div><strong>Escriba origen y destino.</strong><br>Le mostramos qué ruta tomar, dónde bajarse, dónde cambiar y a qué hora pasa su bus.</div></div>`;
}
async function planear(e) {
  e && e.preventDefault();
  const o = norm($("#origen").value.trim()), d = norm($("#destino").value.trim());
  const hora = $("#hora-viaje").value || ahora();
  if (!o || !d) return;
  const r = await api("/api/viaje", { origen: o, destino: d, hora });
  const caja = $("#resultado-viaje");
  if (!r.ok) {
    const msg = {
      no_existe: `No encontramos ${r.estado_origen == null ? "«" + esc(o) + "»" : "«" + esc(d) + "»"}. Use el autocompletado para elegir el nombre exacto.`,
      cerrada: `La estación ${r.estado_origen === "cerrada" ? esc(o) : esc(d)} está cerrada en este momento.`,
      sin_ruta: "No hay viaje directo ni con un solo transbordo entre esas estaciones.",
    }[r.motivo];
    caja.innerHTML = `<div class="vacio-viaje"><svg viewBox="0 0 200 84"><use href="#bus-alimentador"/></svg><div><strong>Sin viaje posible.</strong><br>${msg}</div></div>`;
    return;
  }
  if (r.tramos.length === 0) {
    caja.innerHTML = `<div class="vacio-viaje"><div><strong>Ya está en ${esc(o)}.</strong><br>Origen y destino son la misma estación.</div></div>`;
    return;
  }
  const t = r.tramos;
  let html = `<div class="itinerario"><div class="itinerario__cabeza">
      <span class="ruta-od">${esc(o)} → ${esc(d)}</span>
      <span class="chip">${r.total_paradas} paradas</span>
      <span class="chip ${t.length > 1 ? "chip--am" : ""}">${t.length > 1 ? "1 transbordo" : "Directo"}</span>
      ${t[t.length - 1].llegada ? `<span class="chip">Llega ≈ ${t[t.length - 1].llegada}</span>` : ""}
    </div>`;
  t.forEach((x, i) => {
    if (i > 0) html += `<div class="transbordo"><svg viewBox="0 0 12 24"><use href="#pic-persona"/></svg>Transborde en <b>${esc(x.sube)}</b> a la ruta ${insignia(x.ruta, true)}</div>`;
    html += `<div class="tramo"><div class="tramo__cabeza">${insignia(x.ruta)}
        <div class="tramo__texto"><strong>Suba en ${esc(x.sube)}</strong><div>Bájese en ${esc(x.baja)} · ${x.paradas} parada${x.paradas === 1 ? "" : "s"} · hacia ${esc(x.estaciones[x.estaciones.length - 1].nombre)}</div></div>
        <div class="horas">
          <div class="hora-led">${x.bus || "--:--"}<small>Pasa${x.manana ? " · mañana" : ""}</small></div>
          <div class="hora-led">${x.llegada || "--:--"}<small>Llega</small></div>
        </div></div>
      ${x.bus ? "" : `<p class="nota">Esta ruta ya no pasa por ${esc(x.sube)} después de las ${esc(i === 0 ? r.hora : t[i - 1].llegada || r.hora)}.</p>`}
      <div class="tira-contenedor">${tira(x.estaciones, x.ruta, { bus: true })}</div></div>`;
  });
  caja.innerHTML = html + "</div>";
}

/* ================================================ ESTACIONES (R1, R3, R4) */
async function consultarEstado(e) {
  e && e.preventDefault();
  const n = norm($("#estado-nombre").value.trim());
  if (!n) return;
  const r = await api("/api/estado", { nombre: n });
  const etiqueta = r.estado === "abierta" ? ["ABIERTA", "abierta"] : r.estado === "cerrada" ? ["CERRADA", "cerrada"] : ["NO EXISTE", "no"];
  $("#res-estado").innerHTML = `<div class="letrero"><div class="letrero__nombre">${esc(n)}
      <small>${r.estado ? `${r.buses.toLocaleString("es-CO")} buses al día · ${r.rutas.length} rutas` : "Revise el nombre exacto: mayúsculas y sin tildes."}</small></div>
      <span class="estado estado--${etiqueta[1]}">${etiqueta[0]}</span></div>
      ${r.rutas.length ? `<div class="mini-insignias">${r.rutas.map((x) => insignia(x, true)).join("")}</div>` : ""}`;
}
async function listarRango(e) {
  e && e.preventDefault();
  const a = norm($("#rango-desde").value.trim()), b = norm($("#rango-hasta").value.trim());
  const r = await api("/api/rango", { desde: a, hasta: b });
  $("#res-rango").innerHTML = r.length
    ? r.map((n) => `<span class="baldosa">${esc(n)}</span>`).join("") + `<p class="nota" style="width:100%">${r.length} estaciones abiertas, en orden alfabético (como texto: «CALLE 100» va antes que «CALLE 26»).</p>`
    : `<p class="nota">No hay estaciones abiertas entre «${esc(a)}» y «${esc(b)}».</p>`;
}
async function pantalla(e) {
  e && e.preventDefault();
  const est = norm($("#pantalla-est").value.trim());
  const hora = $("#pantalla-hora").value || ahora();
  if (!est) return;
  const r = await api("/api/pantalla", { estacion: est, hora });
  const cab = `<div class="led__cab"><span>${esc(est)}</span><span>${hora}</span></div>`;
  if (r.estado !== "abierta") {
    $("#pantalla").innerHTML = cab + `<div class="led__vacio">${r.estado === "cerrada" ? "ESTACIÓN CERRADA" : "ESTACIÓN NO ENCONTRADA"}</div>`;
    return;
  }
  $("#pantalla").innerHTML = cab + r.filas.slice(0, 9).map((f) => `
    <div class="led__fila">${insignia(f.ruta, true)}<span>${esc(f.destino)}</span>
      <span>${f.proximo || "--:--"}</span>
      <span class="min ${f.minutos === 0 ? "ya" : ""}">${f.minutos == null ? "—" : f.minutos === 0 ? "YA" : f.minutos + " min"}</span></div>`).join("")
    + (r.filas.length > 9 ? `<div class="led__fila"><span></span><span>+${r.filas.length - 9} rutas más</span></div>` : "");
}
async function cargarRutasDe() {
  const est = norm($("#prox-est").value.trim());
  const r = await api("/api/estado", { nombre: est });
  $("#prox-ruta").innerHTML = r.rutas.length ? r.rutas.map((x) => `<option>${esc(x)}</option>`).join("") : `<option value="">Sin rutas</option>`;
}
async function proximo(e) {
  e.preventDefault();
  const est = norm($("#prox-est").value.trim()), ruta = $("#prox-ruta").value, hora = $("#prox-hora").value || ahora();
  if (!est || !ruta) return;
  const r = await api("/api/proximo", { estacion: est, ruta, hora });
  $("#res-proximo").innerHTML = `<div class="letrero" style="background:#111">${insignia(ruta)}
    <div class="letrero__nombre">${r.hora ? `Próximo bus: ${r.hora}` : "No hay más buses"}<small>${esc(est)} · desde las ${hora}</small></div></div>`;
}

/* ================================================ RANKING (R6) */
async function ranking() {
  const k = +$("#rk-k").value;
  $("#rk-kv").textContent = k;
  const r = await api("/api/ranking", { k });
  const max = r.length ? r[0][1] : 1;
  const orden = [1, 0, 2].filter((i) => r[i]);
  $("#podio").innerHTML = orden.map((i) => `<div class="podio__lugar">${svgBus()}
      <div class="podio__nombre">${esc(r[i][0])}</div><div class="podio__buses">${r[i][1] == null ? "" : r[i][1].toLocaleString("es-CO") + " buses/día"}</div>
      <div class="podio__base">${i + 1}</div></div>`).join("");
  $("#lista-ranking").innerHTML = r.map(([n, b], i) => `<li><span class="pos">${i + 1}</span><span class="nom">${esc(n)}</span>
      <span class="barra-r" style="width:${(b / max) * 100}%;animation-delay:${i * 25}ms"></span><span class="num">${b == null ? "" : b.toLocaleString("es-CO")}</span></li>`).join("");
}

/* ================================================ CONTROL (R7, R8, R9) */
let rutasTodas = [];
const bitacora = [];
function registrar(texto) {
  bitacora.push({ texto, deshecho: false });
  // un cambio nuevo borra lo que había para rehacer (igual que en el motor)
  for (let i = bitacora.length - 2; i >= 0 && bitacora[i].deshecho; i--) bitacora.splice(i, 1);
  pintarBitacora();
}
function pintarBitacora() {
  $("#bitacora").innerHTML = bitacora.length
    ? bitacora.slice().reverse().map((b) => `<li class="${b.deshecho ? "deshecho" : ""}">${b.texto}</li>`).join("")
    : `<li class="vacio">Sin cambios todavía.</li>`;
}
let CAP = { r7: true, r9: true };
function actualizarInfo(i) {
  CAP = { r7: i.r7 !== false, r9: i.r9 !== false };
  $("#n-deshacer").textContent = i.deshacer;
  $("#n-rehacer").textContent = i.rehacer;
  $("#b-deshacer").disabled = !CAP.r9 || i.deshacer === 0;
  $("#b-rehacer").disabled = !CAP.r9 || i.rehacer === 0;
  $("#f-agregar").hidden = !CAP.r7;
  const faltan = [!CAP.r7 && "R7 (editar rutas)", !CAP.r9 && "R9 (deshacer/rehacer)"].filter(Boolean);
  $("#aviso-integracion").hidden = faltan.length === 0;
  $("#aviso-integracion").innerHTML = faltan.length
    ? `<b>Pendiente en el motor:</b> ${faltan.join(" y ")} ya están programados en <code>motor/operar.py</code>, pero la clase <code>Red</code> todavía no los usa. En cuanto se conecten, estos botones funcionan solos.`
    : "";
  $("#lista-cerradas").innerHTML = i.cerradas.length
    ? i.cerradas.map((n) => `<span class="baldosa" style="border-color:#8a949e">${esc(n)}<button data-reabrir="${esc(n)}">Reabrir</button></span>`).join("")
    : `<p class="nota">Todas las estaciones están abiertas.</p>`;
  $("#pie-info").textContent = ` · ${i.estaciones} estaciones, ${i.rutas} rutas`;
}
function filtrarRutas() {
  const f = norm($("#ctl-ruta-filtro").value.trim());
  const sel = $("#ctl-ruta"), actual = sel.value;
  const lista = rutasTodas.filter((r) => r.startsWith(f));
  sel.innerHTML = lista.map((r) => `<option ${r === actual ? "selected" : ""}>${esc(r)}</option>`).join("");
  recorrido();
}
async function recorrido() {
  const ruta = $("#ctl-ruta").value;
  if (!ruta) { $("#ctl-tira").innerHTML = `<p class="nota">No hay rutas con ese filtro.</p>`; return; }
  const reves = $("#ctl-reves").checked;
  const r = await api("/api/recorrido", { ruta, al_reves: reves ? 1 : 0 });
  $("#ctl-tira").innerHTML = `<div class="en-linea" style="margin:10px 0 0">${insignia(ruta)}<strong>${esc(r[0]?.nombre || "")} → ${esc(r[r.length - 1]?.nombre || "")}</strong><span class="nota" style="margin:0">${r.length} paradas${reves ? " · vista en sentido inverso" : ""}</span></div>` + tira(r, ruta, { editable: true });
  const adelante = reves ? r.slice().reverse() : r;
  $("#ag-despues").innerHTML = adelante.map((e) => `<option>${esc(e.nombre)}</option>`).join("");
}
async function cambio(ruta, cuerpo, texto) {
  const r = await post(ruta, cuerpo);
  if (r.ok) { registrar(texto); aviso("Listo: " + texto.replace(/<[^>]+>/g, "")); }
  else aviso("No se pudo: revise los nombres o el estado actual.", true);
  actualizarInfo(r);
  recorrido();
  return r.ok;
}
async function historial(accion) {
  const r = await post("/api/" + accion);
  if (r.ok) {
    if (accion === "deshacer") { const b = [...bitacora].reverse().find((x) => !x.deshecho); if (b) b.deshecho = true; }
    else { const b = bitacora.find((x) => x.deshecho); if (b) b.deshecho = false; }
    pintarBitacora();
    aviso(accion === "deshacer" ? "Cambio deshecho" : "Cambio rehecho");
  }
  actualizarInfo(r);
  recorrido();
}

/* ================================================ HORA PICO (R10) */
let animFila;
async function simularFila(e) {
  e && e.preventDefault();
  cancelAnimationFrame(animFila);
  $("#fila-stats").innerHTML = `<span class="cargando">Simulando…</span>`;
  const r = await api("/api/fila", { pasajeros: $("#fl-p").value, ventana: $("#fl-v").value, frecuencia: $("#fl-f").value, capacidad: $("#fl-c").value, patron: $("#fl-patron").value });
  const f1 = (x) => x.toLocaleString("es-CO", { maximumFractionDigits: 1 });
  $("#fila-stats").innerHTML = [
    [f1(r.buses), "buses despachados"], [f1(r.atendidos), "pasajeros que subieron"],
    [f1(r.espera_promedio) + " min", "espera promedio"], [f1(r.cola_max), "personas en fila (máx.)"],
    [f1(r.en_espera), `siguen esperando a las ${r.fin}`], [r.llenos == null ? "—" : f1(r.llenos), "buses que salieron llenos"],
    [`${r.inicio}–${r.fin}`, "ventana simulada"], [r.ms_motor + " ms", `motor con ${f1(r.pasajeros)} pasajeros`],
  ].map(([b, s]) => `<div class="stat"><b>${b}</b><span>${s}</span></div>`).join("");
  graficaFila(r);
  animarAnden(r);
}
function graficaFila(r) {
  const W = 760, H = 220, P = { l: 56, r: 12, t: 14, b: 30 };
  const s = r.serie, t0 = s[0].t, t1 = s[s.length - 1].t || t0 + 1, ymax = Math.max(1, ...s.map((p) => p.cola));
  const X = (t) => P.l + ((t - t0) / Math.max(1, t1 - t0)) * (W - P.l - P.r), Y = (v) => H - P.b - (v / ymax) * (H - P.t - P.b);
  const camino = s.map((p, i) => `${i ? "L" : "M"}${X(p.t).toFixed(1)},${Y(p.cola).toFixed(1)}`).join("");
  const ticks = [0, .25, .5, .75, 1].map((f) => Math.round(ymax * f));
  const xt = [0, .25, .5, .75, 1].map((f) => s[Math.min(s.length - 1, Math.round((s.length - 1) * f))]);
  $("#fila-grafica").innerHTML = `<svg viewBox="0 0 ${W} ${H}">
    ${ticks.map((v) => `<line x1="${P.l}" x2="${W - P.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="#e6e9ec"/><text x="${P.l - 8}" y="${Y(v) + 4}" text-anchor="end" font-size="11" fill="#5b6570">${v.toLocaleString("es-CO")}</text>`).join("")}
    ${xt.map((p) => `<text x="${X(p.t)}" y="${H - 8}" text-anchor="middle" font-size="11" fill="#5b6570">${p.h}</text>`).join("")}
    <path d="${camino}L${X(t1)},${Y(0)}L${X(t0)},${Y(0)}Z" fill="rgba(200,16,46,.12)"/>
    <path d="${camino}" fill="none" stroke="#c8102e" stroke-width="2"/>
    <line id="cursor-fila" x1="${P.l}" x2="${P.l}" y1="${P.t}" y2="${H - P.b}" stroke="#1f2429" stroke-dasharray="3 3"/>
    <text x="${P.l}" y="10" font-size="11" fill="#5b6570" font-weight="700">Personas esperando después de cada salida</text></svg>`;
  graficaFila.X = X;
}
function animarAnden(r) {
  const s = r.serie, anden = $("#anden"), fila = $("#anden-fila"), bus = $("#anden-bus"), etiqueta = $("#anden-suben");
  const columnas = getComputedStyle(fila).gridTemplateColumns.split(" ").length;
  const capacidad = columnas * 4;                       // 4 filas de figuras caben en el andén
  const ymax = Math.max(1, ...s.map((p) => p.cola + p.suben));
  const porIcono = Math.max(1, Math.ceil(ymax / capacidad));
  // las figuras se crean UNA vez; luego solo se encienden o apagan
  fila.innerHTML = `<svg viewBox="0 0 12 24"><use href="#pic-persona"/></svg>`.repeat(capacidad);
  const hijos = [...fila.children], filas = capacidad / columnas;
  // orden de llenado: fila de abajo primero, empezando junto al bus (la grilla es rtl)
  const figuras = [];
  for (let k = 0; k < capacidad; k++) figuras.push(hijos[(filas - 1 - Math.floor(k / columnas)) * columnas + (k % columnas)]);
  $("#anden-leyenda").textContent = porIcono === 1 ? "cada figura = 1 persona" : `cada figura ≈ ${porIcono} personas`;
  const pintarFila = (personas) => {
    const n = Math.min(capacidad, Math.round(personas / porIcono));
    figuras.forEach((f, k) => f.classList.toggle("on", k < n));
  };

  const CICLO = 1500;                                    // ms por cada salida de bus
  const suave = (x) => 1 - Math.pow(1 - x, 3), acelera = (x) => x * x * x;
  let i = 0, inicio = null, anterior = 0;
  const cuadro = (ts) => {
    animFila = requestAnimationFrame(cuadro);
    if ($("#v-pico").hidden) { inicio = null; return; }  // no animar si la pestaña no está visible
    if (inicio === null) inicio = ts;
    let f = (ts - inicio) / CICLO;
    if (f >= 1) { anterior = s[i].cola; i = (i + 1) % s.length; if (i === 0) anterior = 0; inicio = ts; f = 0; }
    const p = s[i], antes = p.cola + p.suben;           // personas en el andén justo antes de que salga el bus
    const W = anden.clientWidth, wb = bus.offsetWidth;
    const parada = Math.min(W - wb - 8, fila.offsetLeft + fila.offsetWidth - wb * 0.35); // el bus frena frente al inicio de la fila
    let x;
    if (f < 0.35) {                                      // llega gente y el bus entra frenando
      const g = suave(f / 0.35);
      x = -wb - 20 + (parada + wb + 20) * g;
      pintarFila(anterior + (antes - anterior) * (f / 0.35));
      etiqueta.classList.remove("ver");
    } else if (f < 0.72) {                               // la gente sube
      const g = (f - 0.35) / 0.37;
      x = parada;
      pintarFila(antes - p.suben * g);
      etiqueta.textContent = `suben ${p.suben.toLocaleString("es-CO")}`;
      etiqueta.style.left = parada + wb * 0.45 + "px";
      etiqueta.classList.add("ver");
    } else {                                             // el bus arranca y sale
      const g = acelera((f - 0.72) / 0.28);
      x = parada + (W - parada + 20) * g;
      pintarFila(p.cola);
      etiqueta.classList.remove("ver");
    }
    bus.style.transform = `translateX(${x.toFixed(1)}px)`;
    $("#anden-hora").textContent = p.h;
    const c = $("#cursor-fila");
    if (c) { const cx = graficaFila.X(p.t); c.setAttribute("x1", cx); c.setAttribute("x2", cx); }
  };
  animFila = requestAnimationFrame(cuadro);
}

/* ================================================ RENDIMIENTO (R11) */
function graficaRend(op, etiquetas) {
  const W = 320, H = 150, P = { l: 56, r: 30, t: 10, b: 24 };
  const vals = [...op.medido, ...op.esperado], ymax = Math.max(...vals) * 1.12, ymin = 0;
  const X = (i) => P.l + (i / (op.medido.length - 1)) * (W - P.l - P.r);
  const Y = (v) => H - P.b - ((v - ymin) / (ymax - ymin)) * (H - P.t - P.b);
  const linea = (arr) => arr.map((v, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(v).toFixed(1)}`).join("");
  const fmt = (v) => (v >= 1e6 ? (v / 1e6).toFixed(1) + " s" : v >= 1000 ? (v / 1000).toFixed(1) + " ms" : v.toFixed(v < 10 ? 1 : 0) + " µs");
  return `<svg viewBox="0 0 ${W} ${H}">
    ${[0, .5, 1].map((f) => `<line x1="${P.l}" x2="${W - P.r}" y1="${Y(ymax * f / 1.12)}" y2="${Y(ymax * f / 1.12)}" stroke="#eef0f2"/><text x="${P.l - 6}" y="${Y(ymax * f / 1.12) + 4}" text-anchor="end" font-size="10" fill="#8a949e">${fmt(ymax * f / 1.12)}</text>`).join("")}
    ${etiquetas.map((t, i) => `<text x="${X(i)}" y="${H - 6}" text-anchor="middle" font-size="10" fill="#5b6570">${t}</text>`).join("")}
    <path d="${linea(op.esperado)}" fill="none" stroke="#8a949e" stroke-width="2" stroke-dasharray="5 4"/>
    <path d="${linea(op.medido)}" fill="none" stroke="#c8102e" stroke-width="2.5"/>
    ${op.medido.map((v, i) => `<circle cx="${X(i)}" cy="${Y(v)}" r="3.5" fill="#c8102e"><title>${fmt(v)}</title></circle>`).join("")}</svg>`;
}
function pintarRend(r) {
  const etiquetas = r.copias.map((c, i) => `${c}× (${r.tamanos[i].toLocaleString("es-CO")})`);
  $("#rend-sub").textContent = `Mediciones del panel R11 (Front/panel_rendimiento.py) con la red copiada ${r.copias.join(", ")} veces. Línea roja: medido. Punteada: lo que se esperaba. Medido el ${r.fecha}.`;
  $("#rend-grilla").innerHTML = r.operaciones.map((op) => op.pendiente ? `<article class="rend">
      <div class="rend__cab"><span class="req">${op.requisito}</span><code>${esc(op.etiqueta)}</code><span class="rend__o">${esc(op.o)}</span></div>
      <span class="rend__veredicto no" style="align-self:flex-start">Pendiente</span><p>${esc(op.explicacion)}</p></article>` : `<article class="rend">
      <div class="rend__cab"><span class="req">${op.requisito}</span><code>${esc(op.etiqueta)}</code><span class="rend__o">${esc(op.o)}</span></div>
      <div class="rend__n">${esc(op.n)}</div>
      ${graficaRend(op, op.clave === "fila" || op.clave === "carga" ? r.copias.map((c) => c + "×") : etiquetas)}
      <div class="en-linea"><span class="rend__veredicto ${op.coincide ? "ok" : "no"}">${op.coincide ? "Coincide" : "Revisar"}</span>
        <span class="rend__n">Al duplicar: ×${op.razon.toFixed(2)} medido · ×${op.razon_esperada.toFixed(2)} esperado</span></div>
      <p>${esc(op.explicacion)}</p></article>`).join("");
}
async function rendimiento(recalcular = false) {
  if (!recalcular && $("#rend-grilla").children.length) return;
  $("#rend-grilla").innerHTML = `<span class="cargando">${recalcular ? "Midiendo con redes de 1×, 2× y 4× (puede tardar un par de minutos)…" : "Cargando mediciones…"}</span>`;
  $("#b-medir").disabled = true;
  try { pintarRend(recalcular ? await post("/api/rendimiento") : await api("/api/rendimiento")); }
  catch (err) { aviso(err.message, true); }
  $("#b-medir").disabled = false;
}

/* ================================================ arranque */
document.addEventListener("DOMContentLoaded", async () => {
  setInterval(() => ($("#reloj").textContent = ahora()), 1000);
  $("#reloj").textContent = ahora();
  $$("input.ac").forEach(autocompletar);
  ["#hora-viaje", "#pantalla-hora", "#prox-hora"].forEach((s) => ($(s).value = ahora()));

  // planear
  vacioViaje();
  $("#f-viaje").addEventListener("submit", planear);
  $("#intercambiar").addEventListener("click", () => { const a = $("#origen").value; $("#origen").value = $("#destino").value; $("#destino").value = a; });
  $$(".sugeridos button").forEach((b) => b.addEventListener("click", () => { $("#origen").value = b.dataset.o; $("#destino").value = b.dataset.d; planear(); }));

  // estaciones
  $("#f-estado").addEventListener("submit", consultarEstado);
  $("#f-rango").addEventListener("submit", listarRango);
  $("#f-pantalla").addEventListener("submit", pantalla);
  $("#f-proximo").addEventListener("submit", proximo);
  $("#prox-est").addEventListener("elegido", cargarRutasDe);
  $("#prox-est").addEventListener("change", cargarRutasDe);
  cargadores.estaciones = () => { if (!$("#pantalla").innerHTML) { pantalla(); listarRango(); } };

  // ranking
  $("#rk-k").addEventListener("input", ranking);
  cargadores.ranking = ranking;

  // control
  rutasTodas = await api("/api/rutas");
  $("#ctl-ruta-filtro").addEventListener("input", filtrarRutas);
  $("#ctl-ruta").addEventListener("change", recorrido);
  $("#ctl-reves").addEventListener("change", recorrido);
  cargadores.control = async () => { if (!$("#ctl-ruta").options.length) { $("#ctl-ruta-filtro").value = "B"; filtrarRutas(); } };
  $("#ctl-tira").addEventListener("click", (e) => {
    const b = e.target.closest("[data-quitar]");
    if (b) { const ruta = $("#ctl-ruta").value; cambio("/api/quitar", { ruta, estacion: b.dataset.quitar }, `Ruta <b>${esc(ruta)}</b>: se quitó ${esc(b.dataset.quitar)}`); }
  });
  $("#f-agregar").addEventListener("submit", (e) => {
    e.preventDefault();
    const ruta = $("#ctl-ruta").value, nueva = norm($("#ag-nueva").value.trim()), despues = $("#ag-despues").value;
    if (nueva) cambio("/api/agregar", { ruta, nueva, despues_de: despues }, `Ruta <b>${esc(ruta)}</b>: ${esc(nueva)} después de ${esc(despues)}`).then((ok) => ok && ($("#ag-nueva").value = ""));
  });
  $("#f-cerrar").addEventListener("submit", (e) => e.preventDefault());
  $$("#f-cerrar [data-accion]").forEach((b) => b.addEventListener("click", () => {
    const n = norm($("#cerrar-nombre").value.trim());
    if (n) cambio("/api/" + b.dataset.accion, { nombre: n }, `${b.dataset.accion === "cerrar" ? "Se cerró" : "Se reabrió"} <b>${esc(n)}</b>`);
  }));
  $("#lista-cerradas").addEventListener("click", (e) => {
    const b = e.target.closest("[data-reabrir]");
    if (b) cambio("/api/reabrir", { nombre: b.dataset.reabrir }, `Se reabrió <b>${esc(b.dataset.reabrir)}</b>`);
  });
  $("#b-deshacer").addEventListener("click", () => historial("deshacer"));
  $("#b-rehacer").addEventListener("click", () => historial("rehacer"));
  document.addEventListener("keydown", (e) => {
    if (location.hash !== "#control" || !(e.ctrlKey || e.metaKey) || e.target.matches("input")) return;
    if (e.key.toLowerCase() === "z") { e.preventDefault(); historial(e.shiftKey ? "rehacer" : "deshacer"); }
    if (e.key.toLowerCase() === "y") { e.preventDefault(); historial("rehacer"); }
  });
  actualizarInfo(await api("/api/info"));

  // hora pico
  $("#f-fila").addEventListener("submit", simularFila);
  cargadores.pico = () => { if (!$("#fila-stats").innerHTML) simularFila(); };

  // rendimiento
  cargadores.rendimiento = () => rendimiento(false);
  $("#b-medir").addEventListener("click", () => rendimiento(true));

  mostrar(location.hash.slice(1) || "planear");
});
