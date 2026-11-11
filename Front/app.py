import base64  # Convierte la ilustración local en texto para usarla como fondo sin internet.
import html  # Escapa los nombres que vienen de los CSV antes de meterlos en HTML.
import json  # Pasa estaciones, vías y el recorrido de Python a JavaScript (Leaflet).
import sys  # Permite agregar la carpeta raíz a la lista de rutas de importación.
import textwrap  # Parte las etiquetas largas de las estaciones en varias líneas.
from pathlib import Path  # Maneja rutas de archivos sin depender del sistema operativo.
import streamlit as st  # Construye la interfaz web.
import streamlit.components.v1 as components  # Incrusta HTML propio (esquema SVG y mapa Leaflet).

RAIZ = Path(__file__).resolve().parent.parent  # Carpeta principal del proyecto (Front/app.py → raíz).
sys.path.insert(0, str(RAIZ))  # Así Python encuentra los paquetes motor y Front.
from motor.viajes import IndiceViajes, cargar_estaciones, cargar_rutas, buscar_mejor_viaje, detalle_recorrido  # Motor R5.
from Front.geografia import cargar_capas, preparar_estaciones  # Capas geográficas, usadas solo para el mapa.

st.set_page_config(page_title="RutaViva | TransMilenio", page_icon="🚌", layout="wide", initial_sidebar_state="collapsed")  # Pestaña.
imagen_base64 = base64.b64encode((RAIZ / "Assets" / "ciudad.svg").read_bytes()).decode("ascii")  # Ilustración en base64.

# Hoja de estilos de la página (las llaves dobles {{ }} son llaves literales dentro del f-string).
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap'); /* Fuentes. */
html,body,[class*="css"],.stApp {{ font-family:'DM Sans',sans-serif; }} /* Fuente base de toda la app. */
.stApp {{ color:#1e2834;background:linear-gradient(155deg,#fff9f9 0%,#ffffff 45%,#f5f7fa 100%); }} /* Fondo claro degradado. */
.block-container {{ max-width:1260px;padding-top:1.3rem; }} /* Ancho máximo del contenido. */
header[data-testid="stHeader"] {{ background:transparent; }} /* Barra superior de Streamlit transparente. */
.hero {{ position:relative;min-height:265px;padding:30px 36px;border-radius:24px;overflow:hidden;margin-bottom:21px;background:linear-gradient(90deg,rgba(32,39,52,.94),rgba(32,39,52,.82) 45%,rgba(32,39,52,.18)),url('data:image/svg+xml;base64,{imagen_base64}') center right/cover no-repeat;box-shadow:0 15px 32px #26354b20; }} /* Encabezado con ilustración. */
.eyebrow {{ color:#ffdfe0;font-weight:800;letter-spacing:.12em;font-size:12px;margin:9px 0; }} /* Texto pequeño sobre el título. */
.hero h1 {{ color:white;font-family:Outfit,sans-serif;font-size:clamp(34px,4vw,58px);line-height:1.1;margin:4px 0 12px; }} /* Título grande. */
.hero h1 em {{ color:#ff6a74;font-style:normal; }} /* Parte resaltada del título. */
.hero p {{ color:#f1f2f3;font-size:16px;max-width:640px; }} /* Descripción del encabezado. */
.official-logo {{ position:absolute;right:28px;top:25px;width:110px;max-height:80px;object-fit:contain;border-radius:10px;background:#fffefeee;padding:7px; }} /* Logo. */
.brandline {{ display:flex;align-items:center;gap:10px;color:white;font-weight:800; }} /* Línea de marca. */
.brand-square {{ padding:9px;background:#e63845;color:white;border-radius:10px; }} /* Cuadro rojo "TM". */
.pill {{ display:inline-block;color:#fff;border:1px solid #ef9da5;background:#cd3d50b9;border-radius:30px;padding:6px 13px;font-size:12px; }} /* Etiqueta. */
.sectionhead {{ font-family:Outfit,sans-serif;font-size:25px;font-weight:800;color:#263445;margin-top:17px; }} /* Títulos de sección. */
.subtitle {{ color:#526378;margin-bottom:15px; }} /* Subtítulos. */
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:20px; }} /* Bordes redondeados de contenedores. */
[data-testid="stSelectbox"] label,[data-testid="stRadio"] label {{ color:#2a3645!important;font-weight:700; }} /* Etiquetas de controles. */
div[data-baseweb="select"]>div {{ background:white;border:1px solid #d9e1e8;border-radius:12px;min-height:48px; }} /* Cajas de selección. */
div[data-testid="stRadio"] {{ background:#fff;border:1px solid #e0e5eb;border-radius:14px;padding:13px 16px 3px; }} /* Botones de opción. */
.stButton>button {{ background:linear-gradient(105deg,#e53446,#c81e33);color:white;border:0;border-radius:12px;font-weight:800;padding:.65rem 1.2rem; }} /* Botones. */
.stButton>button:hover {{ background:#b91e30;color:white; }} /* Botón al pasar el mouse. */
div[data-testid="stMetric"] {{ background:white;border:1px solid #e2e6ed;border-radius:14px;padding:12px 16px; }} /* Tarjetas de métricas. */
div[data-testid="stMetricValue"] {{ color:#243247; }} /* Número de las métricas. */
.credit {{ border-radius:12px;padding:14px 16px;background:#fff;border:1px solid #e1e6ed;color:#697887;margin-top:24px;font-size:12px; }} /* Créditos. */
</style>""", unsafe_allow_html=True)  # Inyectamos el CSS en la página.


@st.cache_resource  # Guarda la red en memoria: cada carpeta se carga una sola vez por servidor.
def preparar_red(nombre_carpeta):  # Carga estaciones, rutas e índice de una carpeta de datos.
    carpeta = str(RAIZ / nombre_carpeta)  # Ruta completa de la carpeta elegida.
    estaciones, rutas = cargar_estaciones(carpeta), cargar_rutas(carpeta)  # Leemos los dos CSV con el motor.
    return estaciones, rutas, IndiceViajes(rutas, estaciones)  # Devolvemos todo con el índice ya construido.


@st.cache_data(ttl=3600, show_spinner=False)  # Guarda las capas una hora para no consultar los servidores a cada rato.
def obtener_mapa_oficial(actualizar=False):  # Descarga (o reutiliza) estaciones y troncales oficiales.
    return cargar_capas(RAIZ / "Datos", actualizar)  # La descarga vive en Front/geografia.py.


def mapa_esquematico(detalle):  # Dibuja en SVG el orden de paradas del viaje (no es un mapa geográfico).
    if not detalle:  # Si el motor no entregó paradas...
        st.info("No fue posible reconstruir la secuencia de estaciones.")  # ...avisamos sin inventar datos...
        return  # ...y no dibujamos nada.
    colores = ["#fc5261", "#44c6c6"]  # Un color por servicio: primer y segundo bus.
    ancho = 170 * max(len(tramo[1]) for tramo in detalle)  # 170 px por estación del tramo más largo.
    alto = 180 if len(detalle) == 1 else 325  # Altura para uno o dos servicios.
    partes = [f'<svg width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg">']  # Abrimos el SVG.
    for num, (servicio, paradas) in enumerate(detalle):  # Cada tramo llega como [servicio, [estaciones]].
        y, color = 78 + num * 145, colores[num % len(colores)]  # Altura de la fila y color del servicio.
        fin = 70 + 170 * (len(paradas) - 1)  # Coordenada x de la última parada.
        partes.append(f'<line x1="70" y1="{y}" x2="{fin}" y2="{y}" stroke="{color}" stroke-width="9" stroke-linecap="round"/>')  # Línea del tramo.
        partes.append(f'<text x="70" y="{y-46}" fill="{color}" font-size="16" font-weight="700">SERVICIO {html.escape(str(servicio))}</text>')  # Nombre del servicio.
        for i, nombre in enumerate(paradas):  # Recorremos las paradas en el orden recibido.
            x, especial = 70 + i * 170, i == 0 or i == len(paradas) - 1  # Posición fija (no es distancia real); extremos destacados.
            partes.append(f'<circle cx="{x}" cy="{y}" r="{13 if especial else 9}" fill="{color if especial else "#202d3b"}" stroke="{color}" stroke-width="4"/>')  # Parada.
            lineas = textwrap.wrap(str(nombre), 18, break_long_words=False, break_on_hyphens=False)  # Etiqueta en líneas de máx. 18 caracteres.
            for n, linea in enumerate(lineas[:3]):  # Máximo tres líneas por etiqueta.
                partes.append(f'<text x="{x}" y="{y+31+n*16}" text-anchor="middle" fill="#e5ecf4" font-size="12" font-weight="600">{html.escape(linea)}</text>')  # Texto.
    partes.append("</svg>")  # Cerramos el SVG.
    fondo = "background-color:#1d2a3a;background-image:linear-gradient(#ffffff06 1px,transparent 1px),linear-gradient(90deg,#ffffff06 1px,transparent 1px);background-size:24px 24px;"  # Cuadrícula tipo mapa.
    components.html(  # Mostramos el SVG en un panel con desplazamiento horizontal.
        f'<html><body style="margin:0;background:#172232;color:white;font-family:Arial,sans-serif;">'  # Fondo oscuro.
        f'<div style="border:1px solid #405164;border-radius:18px;overflow-x:auto;padding:10px;{fondo}">{"".join(partes)}</div>'  # Panel con scroll.
        f'<p style="color:#9baaba;font-size:12px;margin:8px 0 0 5px;">↔ Desliza para ver todas las estaciones · Esquema del orden de paradas, no un mapa geográfico.</p></body></html>',  # Nota.
        height=alto + 83, scrolling=False)  # Alto del panel.


def mostrar_viaje(resultado, titulo, rutas, indice, origen, destino, cerradas):  # Muestra el resumen y el esquema de un viaje.
    st.markdown(f'<div class="sectionhead">{html.escape(titulo)}</div>', unsafe_allow_html=True)  # Título del panel.
    if resultado is None:  # El motor no encontró viaje...
        st.warning("No encontramos un viaje válido con máximo un transbordo.")  # ...lo avisamos...
        return  # ...y terminamos.
    if resultado[0] == "ERROR":  # Validación fallida (estación inexistente o cerrada)...
        st.error(resultado[1])  # ...mostramos el mensaje del motor...
        return  # ...y terminamos.
    if resultado[0] == "MISMO DESTINO":  # Origen y destino iguales...
        st.success("¡Ya estás en tu destino! No necesitas abordar un bus.")  # ...no hay que tomar bus...
        return  # ...y terminamos.
    cambios = 1 if resultado[0] == "TRANSBORDO" else 0  # Número de transbordos del viaje.
    a, b = st.columns(2)  # Dos columnas para las métricas.
    a.metric("🚏 Tramos", resultado[4])  # Tramos entre estaciones.
    b.metric("🔄 Transbordos", cambios)  # Cambios de servicio.
    st.markdown(f"**🚌 Toma el servicio:** `{html.escape(str(resultado[1]))}`")  # Primer servicio.
    if cambios:  # Si hay transbordo, decimos dónde y a qué servicio...
        st.markdown(f"**🔁 Cambia en:** {html.escape(str(resultado[3]))} → **Servicio** `{html.escape(str(resultado[2]))}`")  # ...cambiar.
    else:  # Si es directo...
        st.markdown("**✅ Sin transbordos:** permanece en el mismo servicio.")  # ...no hay que bajarse antes.
    detalle = detalle_recorrido(rutas, indice, resultado, origen, destino, cerradas)  # El motor entrega las paradas exactas.
    if detalle:  # Solo dibujamos si hay itinerario.
        st.markdown("**🗺️ Tu recorrido, estación por estación**")  # Encabezado del esquema.
        mapa_esquematico(detalle)  # Dibujamos el SVG.
        with st.expander("📋 Ver instrucciones paso a paso", expanded=False):  # Versión en texto (accesibilidad y sustentación).
            pasos = [f"Sube al servicio **{detalle[0][0]}** en **{origen}**."]  # Primer paso: abordar en el origen.
            if len(detalle) == 2:  # Si hay transbordo, agregamos el cambio de bus.
                pasos.append(f"Baja en **{resultado[3]}** y cambia al servicio **{detalle[1][0]}**.")  # Paso del transbordo.
            pasos.append(f"Baja en **{destino}**.")  # Último paso: bajarse en el destino.
            for n, paso in enumerate(pasos, 1):  # Numeramos los pasos desde 1.
                st.write(f"**{n}.** {paso}")  # Escribimos cada paso.
            for servicio, paradas in detalle:  # Listamos las paradas de cada servicio.
                st.write(f"**Servicio {servicio}:** " + " → ".join(paradas))  # Secuencia real de estaciones.


def pintar_mapa(puntos, troncales, servicios, seleccion, origen, destino, transbordo):  # Mapa Leaflet con estaciones y troncales oficiales.
    html_mapa = r'''<!DOCTYPE html><html lang="es"><head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"> <!-- Codificación y ancho móvil. -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"> <!-- Estilos de Leaflet. -->
    <style>
      *{box-sizing:border-box}html,body{margin:0;background:#fff;font-family:Arial,Helvetica,sans-serif;color:#263445} /* Base. */
      #map{height:490px;width:100%;border-radius:18px;overflow:hidden;background:#eef1f5} /* Contenedor del mapa. */
      #info{margin-top:12px;padding:14px 18px;min-height:56px;border:1px solid #e5e9f0;border-radius:14px;background:#fff;color:#334155;font-size:14px;line-height:1.55} /* Caja de información. */
      .legenda{display:flex;gap:18px;flex-wrap:wrap;margin:10px 0 0 3px;color:#64748b;font-size:12px} /* Leyenda. */
      .bolita{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:middle;margin-right:5px} /* Puntos de la leyenda. */
      .leaflet-popup-content{margin:0!important;line-height:1.5;font-size:13px;min-width:245px;max-width:315px} /* Contenido del popup. */
      .leaflet-popup-content-wrapper{border-radius:17px;padding:0;box-shadow:0 12px 35px #10182825;overflow:hidden} /* Marco del popup. */
      .leaflet-container{font-family:Arial,sans-serif} /* Fuente del mapa. */
      .rv-card{padding:17px 18px 16px;color:#263445;background:#fff} /* Tarjeta de estación. */
      .rv-card .rv-kicker{color:#d93649;font-size:10px;letter-spacing:.1em;text-transform:uppercase;font-weight:800;margin-bottom:5px} /* Rótulo. */
      .rv-card .rv-name{font-size:18px;font-weight:800;line-height:1.22;color:#182331;margin-bottom:9px} /* Nombre de la estación. */
      .rv-card .rv-address{font-size:12px;color:#64748b;line-height:1.45;margin-bottom:13px} /* Dirección. */
      .rv-card .rv-section{font-size:12px;color:#334155;font-weight:750;margin-bottom:7px} /* Subtítulo de servicios. */
      .rv-card .rv-badges{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px} /* Grupo de etiquetas. */
      .rv-card .rv-badge{background:#fff0f1;border:1px solid #fbd5da;border-radius:7px;padding:3px 7px;color:#a92337;font-size:11px;font-weight:750} /* Etiqueta de servicio. */
      .rv-card .rv-note{font-size:10px;color:#8190a2;line-height:1.4;margin:8px 0 0} /* Nota aclaratoria. */
      .rv-card .rv-details{border-top:1px solid #edf0f4;margin-top:11px;padding-top:9px} /* Bloque desplegable. */
      .rv-card .rv-details summary{font-size:11px;color:#64748b;cursor:pointer;font-weight:650} /* Título del desplegable. */
      .rv-card .rv-details div{font-size:11px;color:#475569;margin-top:7px;word-break:break-word} /* Contenido del desplegable. */
      .rv-card .rv-status{background:#e8f7f0;color:#18744e;display:inline-block;font-size:11px;padding:4px 8px;border-radius:999px;margin:3px 5px 5px 0;font-weight:750} /* Estado. */
      .rv-card .rv-muted{color:#64748b;font-size:12px} /* Texto secundario. */
    </style></head><body>
    <div id="map"></div> <!-- Aquí se dibuja el mapa. -->
    <div class="legenda"><span><i class="bolita" style="background:#e63946"></i>Estación del recorrido</span><span><i class="bolita" style="background:#0891b2"></i>Estación de transbordo</span><span><i class="bolita" style="background:#78889b"></i>Otras estaciones</span><span>━ Corredores geográficos oficiales</span></div> <!-- Leyenda. -->
    <div id="info">🚏 Selecciona una estación o una línea troncal para conocer sus datos.</div> <!-- Caja de información. -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
    const estaciones=__PUNTOS__, troncales=__TRONCALES__, servicios=__SERVICIOS__, seleccion=__SELECCION__, focos=__FOCOS__; // Datos enviados desde Python.
    const mapa=L.map('map',{preferCanvas:true}).setView([4.653,-74.094],11); // Mapa centrado en Bogotá.
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors',maxZoom:18}).addTo(mapa); // Mapa base.
    const caja=document.getElementById('info'); // Caja donde se muestra la información al hacer clic.
    function escapar(v){return String(v===undefined?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));} // Texto seguro para HTML.
    function dato(prop,nombre){const k=Object.keys(prop||{}).find(k=>k.toLowerCase()===nombre.toLowerCase());return k?prop[k]:'';} // Lee una propiedad sin importar mayúsculas.
    const estacionesElegidas=new Set(seleccion); const tramosMarcados=[]; // Estaciones del viaje y sus coordenadas.
    if(troncales.features && troncales.features.length){ // Si hay corredores oficiales, los dibujamos (infraestructura, no un bus específico).
      L.geoJSON(troncales,{style:()=>({color:'#b84252',weight:3,opacity:.55}),onEachFeature:(f,capa)=>{ // Estilo de cada corredor.
        const p=f.properties||{}, troncal=dato(p,'nom_tronc')||'Troncal', trazado=dato(p,'nom_traz')||'Tramo'; // Nombre de troncal y tramo.
        const mensaje='<strong>🛣️ '+escapar(troncal)+'</strong><br>Tramo: '+escapar(trazado)+'<br><small>Infraestructura geográfica; no confirma servicios en tiempo real.</small>'; // Texto.
        capa.bindPopup(mensaje); // Popup al hacer clic.
        capa.on('click',()=>{caja.innerHTML=mensaje;}); // Copiamos el texto a la caja de información.
        capa.on('mouseover',()=>{capa.setStyle({weight:6,opacity:.95});}); // Resaltamos al pasar el mouse.
        capa.on('mouseout',()=>{capa.setStyle({weight:3,opacity:.55});}); // Volvemos al estilo normal.
      }}).addTo(mapa); // Agregamos la capa al mapa.
    }
    for(const p of estaciones){ // Recorremos cada estación oficial.
      const clave=p.historico||''; // Nombre equivalente en el CSV (vacío si no hubo coincidencia).
      const incluida=estacionesElegidas.has(clave); // ¿Está en el recorrido?
      const esCambio=clave && clave===focos.transbordo, esOrigen=clave && clave===focos.origen, esDestino=clave && clave===focos.destino; // Roles.
      const color=esCambio?'#0891b2':incluida?'#e63946':'#78889b'; // Color según el rol.
      const marcador=L.circleMarker([p.lat,p.lon],{radius:esCambio?10:(incluida?8:4),color:'#ffffff',weight:1.5,fillColor:color,fillOpacity:.93}).addTo(mapa); // Punto.
      const lista=servicios[clave]||[]; // Servicios que pasan por la estación.
      const etiquetas=lista.slice(0,10).map(c=>'<span class="rv-badge">'+escapar(c)+'</span>').join(''); // Hasta 10 etiquetas.
      const extra=lista.length>10?'<span class="rv-badge">+'+(lista.length-10)+' más</span>':''; // Contador del resto.
      let texto='<div class="rv-card"><div class="rv-kicker">🚏 Estación TransMilenio</div><div class="rv-name">'+escapar(p.nombre)+'</div>'; // Encabezado de la tarjeta.
      if(p.ubicacion){texto+='<div class="rv-address">📍 '+escapar(p.ubicacion)+'</div>';} // Dirección, si existe.
      if(esOrigen)texto+='<span class="rv-status">🟢 Tu origen</span>'; // Marca de origen.
      if(esDestino)texto+='<span class="rv-status">🏁 Tu destino</span>'; // Marca de destino.
      if(esCambio)texto+='<span class="rv-status">🔄 Transbordo</span>'; // Marca de transbordo.
      if(incluida && !esOrigen && !esDestino && !esCambio)texto+='<span class="rv-status">✓ En tu recorrido</span>'; // Parada intermedia.
      if(clave && lista.length){ // Si tiene servicios asociados, los listamos.
        texto+='<div class="rv-section">🚌 Servicios asociados <span class="rv-muted">('+lista.length+')</span></div><div class="rv-badges">'+etiquetas+extra+'</div>'; // Etiquetas.
        texto+='<div class="rv-note">Servicios del conjunto de datos seleccionado. Información de referencia; no garantiza operación actual.</div>'; // Aclaración.
      }else if(clave){ // Coincide con el CSV pero sin servicios.
        texto+='<div class="rv-muted">No hay servicios asociados en el conjunto de datos seleccionado.</div>'; // Aviso.
      }else{ // No coincide con ninguna estación del CSV.
        texto+='<div class="rv-muted">Esta estación no tiene una coincidencia confirmada en el conjunto de datos seleccionado.</div>'; // Aviso.
      }
      if(clave){texto+='<details class="rv-details"><summary>Ver referencia del conjunto de datos</summary><div>'+escapar(clave)+' · 2021</div></details>';} // Referencia.
      texto+='</div>'; // Cerramos la tarjeta.
      marcador.bindPopup(texto,{maxWidth:335}); // Popup de la estación.
      marcador.on('click',()=>{caja.innerHTML=texto;}); // Copiamos la tarjeta a la caja de información.
      if(incluida){tramosMarcados.push([p.lat,p.lon]);} // Guardamos coordenadas del recorrido para el zoom.
    }
    if(tramosMarcados.length){mapa.fitBounds(L.latLngBounds(tramosMarcados).pad(.23),{maxZoom:14});} // Acercamos el mapa al recorrido.
    if(!estaciones.length && !((troncales.features||[]).length)){ // Si no llegó ninguna capa oficial...
      caja.textContent='🗺️ Mapa de Bogotá disponible. Las capas de estaciones y corredores se cargarán cuando el servidor de datos permita la conexión.'; // ...lo avisamos.
    }
    </script></body></html>'''  # Fin de la plantilla; los marcadores __X__ se reemplazan abajo.
    datos = {"__PUNTOS__": puntos, "__TRONCALES__": troncales, "__SERVICIOS__": servicios, "__SELECCION__": seleccion,  # Datos para JavaScript...
             "__FOCOS__": {"origen": origen, "destino": destino, "transbordo": transbordo}}  # ...incluidos origen, destino y transbordo.
    for marcador, valor in datos.items():  # Reemplazamos cada marcador por su JSON.
        html_mapa = html_mapa.replace(marcador, json.dumps(valor, ensure_ascii=False).replace("</", "<\\/"))  # "<\/" evita cerrar el <script> por error.
    components.html(html_mapa, height=615, scrolling=False)  # Mostramos el mapa interactivo.


# ---------------- ENCABEZADO Y SELECCIÓN DE DATOS ----------------
st.markdown('<section class="hero"><img class="official-logo" src="https://commons.wikimedia.org/wiki/Special:FilePath/TransMilenio%20S.%20A.%20Bogot%C3%A1%20logo.svg" alt="Logotipo institucional de TransMilenio"/>'  # Logo.
            '<div class="brandline"><span class="brand-square">TM</span><span>RUTAVIVA · PLANIFICADOR</span></div><div class="eyebrow">MUÉVETE MEJOR POR BOGOTÁ</div>'  # Marca.
            '<h1>Tu ciudad.<br><em>Tu mejor ruta.</em></h1><p>Encuentra conexiones entre estaciones, compara opciones y descubre dónde hacer transbordo.</p>'  # Título.
            '<span class="pill">🚌 Datos históricos · Red académica TransMilenio</span></section>', unsafe_allow_html=True)  # Etiqueta y cierre del encabezado.
st.markdown('<div class="sectionhead">Planea tu próximo recorrido</div>', unsafe_allow_html=True)  # Título de la búsqueda.
st.markdown('<div class="subtitle">Elige tu origen, destino y cómo quieres viajar.</div>', unsafe_allow_html=True)  # Instrucción.

FUENTES = ["Datos académicos del profesor (2021)", "Datos GTFS convertidos (2026)"]  # Conjuntos de datos disponibles.
fuente = st.selectbox("🗂️ ¿Qué datos quieres utilizar?", FUENTES)  # El usuario elige uno.
nombre_carpeta = "Datos" if fuente == FUENTES[0] else "Datos_corregidos"  # Carpeta que corresponde a esa fuente.
faltantes = [a for a in ["estaciones.csv", "rutas.csv", "horarios.csv"] if not (RAIZ / nombre_carpeta / a).is_file()]  # Archivos que no existen.
if faltantes:  # Si falta alguno, avisamos en vez de dejar que el programa falle.
    st.markdown('<div style="background-color:#FFF3CD;color:#664D03;padding:16px;border-radius:10px;border:1px solid #FFECB5;font-weight:600;">'  # Caja amarilla...
                "⚠️ Los datos seleccionados todavía no están completos.</div>", unsafe_allow_html=True)  # ...con el aviso.
    st.info("Archivos faltantes: " + ", ".join(faltantes))  # Decimos cuáles faltan.
    if nombre_carpeta == "Datos_corregidos":  # Para GTFS explicamos cómo generarlos.
        st.markdown("Para utilizar los datos GTFS, primero debes generar los archivos con el conversor incluido en el proyecto. Consulta las instrucciones del README.")  # Ayuda.
    else:  # Para los datos del profesor es un error real.
        st.error("Faltan archivos del conjunto académico del profesor.")  # Error.
    st.stop()  # Detenemos esta ejecución de la página.

estaciones, rutas, indice = preparar_red(nombre_carpeta)  # Cargamos la red (desde caché si ya estaba).
cerradas = ["CALLE 57"]  # Cierre provisional para la demostración.

# ---------------- PLANEADOR ----------------
col1, col2 = st.columns(2, gap="medium")  # Dos columnas para origen y destino.
origen = col1.selectbox("📍 Estación de origen", estaciones)  # Origen a la izquierda.
destino = col2.selectbox("🏁 Estación de destino", estaciones, index=1 if len(estaciones) > 1 else 0)  # Destino a la derecha.
modo = st.radio("¿Qué prefieres?", ["Menos paradas", "Menos transbordos", "Comparar ambas"], horizontal=True)  # Criterio de búsqueda.
st.caption("Datos históricos para demostración · CALLE 57 está cerrada solo en esta simulación.")  # Aviso del cierre simulado.
resultado_mapa = None  # Viaje que se resaltará en el mapa geográfico (si hay uno).
if st.button("🔎 Encontrar mi ruta", type="primary", use_container_width=True):  # Solo buscamos al presionar el botón.
    if modo == "Comparar ambas":  # Comparación: dos búsquedas, una debajo de la otra.
        opciones = [["paradas", "🏆 Opción 1 · Menos paradas"], ["transbordos", "🔁 Opción 2 · Menos transbordos"]]  # Criterio y título de cada una.
    else:  # Un solo criterio.
        opciones = [["paradas" if modo == "Menos paradas" else "transbordos", "🗺️ Recorrido recomendado"]]  # Traducimos la opción al criterio del motor.
    for n, (criterio, titulo) in enumerate(opciones):  # Ejecutamos cada búsqueda.
        if n > 0:  # Entre dos resultados ponemos una línea divisoria.
            st.divider()  # Separador.
        resultado = buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice, criterio)  # El motor calcula el viaje.
        if n == 0:  # El primer resultado (menos paradas al comparar) es el que va al mapa.
            resultado_mapa = resultado  # Lo guardamos para el mapa.
        mostrar_viaje(resultado, titulo, rutas, indice, origen, destino, cerradas)  # Mostramos el viaje.
st.markdown('<div class="credit">Proyecto académico independiente · Datos históricos, no información en tiempo real · El esquema muestra el orden de paradas, NO su ubicación física ni distancias. '
            'Para un mapa geográfico se requieren coordenadas verificadas de cada estación.</div>', unsafe_allow_html=True)  # Nota de alcance.

# ---------------- MAPA OFICIAL (CAPA DEL FRONT, NO DEL MOTOR R5) ----------------
st.markdown('<div class="sectionhead">🗺️ Explora las estaciones y troncales</div>', unsafe_allow_html=True)  # Título de la sección.
col_mapa, col_accion = st.columns([4, 1], vertical_alignment="center")  # Columna de texto y columna del botón.
col_mapa.caption("Toca una estación o una línea roja para consultar sus datos y explorar Bogotá.")  # Instrucción.
actualizar_mapa = col_accion.button("↻ Actualizar mapa", use_container_width=True)  # Botón para refrescar las capas.
if actualizar_mapa:  # Si se pidió actualizar...
    obtener_mapa_oficial.clear()  # ...borramos la copia en caché.
estaciones_geo, troncales_geo = obtener_mapa_oficial(actualizar_mapa)  # Capas oficiales (de caché o descargadas).
puntos = preparar_estaciones(estaciones_geo, estaciones)  # Cruzamos estaciones oficiales con los nombres del CSV.

servicios_por_estacion = {}  # Índice informativo estación → servicios (NO se usa para calcular rutas).
for servicio, paradas in rutas:  # Recorremos cada servicio del CSV.
    for _, nombre in paradas:  # Recorremos sus paradas ([orden, estación]).
        lista = servicios_por_estacion.setdefault(nombre, [])  # Lista de la estación (se crea si no existe).
        if servicio not in lista:  # Evitamos servicios repetidos.
            lista.append(servicio)  # Agregamos el servicio.

nombres_recorrido, transbordo_seleccionado = [], ""  # Estaciones a resaltar y estación de cambio.
if resultado_mapa is not None and resultado_mapa[0] not in ("ERROR", "MISMO DESTINO"):  # Solo si hay un viaje real.
    for _, paradas in detalle_recorrido(rutas, indice, resultado_mapa, origen, destino, cerradas):  # Tramos que entrega el motor.
        for nombre in paradas:  # Estaciones de cada tramo.
            if nombre not in nombres_recorrido:  # Sin repetir (la de transbordo aparece en ambos tramos).
                nombres_recorrido.append(nombre)  # La agregamos.
    if resultado_mapa[0] == "TRANSBORDO":  # Si hay cambio de bus...
        transbordo_seleccionado = resultado_mapa[3]  # ...guardamos la estación de transbordo.

hay_viaje = len(nombres_recorrido) > 0  # Solo marcamos origen y destino si hay recorrido.
pintar_mapa(puntos, troncales_geo, servicios_por_estacion, nombres_recorrido,  # Dibujamos el mapa con el recorrido...
            origen if hay_viaje else "", destino if hay_viaje else "", transbordo_seleccionado)  # ...y sus estaciones clave.
st.caption("Mapa geográfico oficial: consulta de estaciones y troncales. Servicios y viajes: CSV académico histórico de 2021. No son datos en tiempo real.")  # Nota de fechas.
st.markdown('<div class="credit">RutaViva · Planeador independiente. Ubicaciones y trazados: TransMilenio / Datos Abiertos Bogotá (CC BY 4.0). Mapa base © OpenStreetMap. '
            'Los tramos geográficos no prueban el recorrido exacto de cada servicio histórico.</div>', unsafe_allow_html=True)  # Créditos finales.