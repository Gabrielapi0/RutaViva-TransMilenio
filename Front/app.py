# Importamos base64 para incluir la ilustración local en el fondo de la página.
import base64
# Importamos html para mostrar nombres provenientes de CSV con seguridad.
import html
# Importamos sys para encontrar la carpeta del motor.
import sys
# Importamos Path para localizar los archivos del proyecto.
from pathlib import Path
# Importamos Streamlit para construir la interfaz de la página.
import streamlit as st
# Importamos componentes para mostrar el esquema SVG interactivo con desplazamiento.
import streamlit.components.v1 as components

# Localizamos la carpeta principal desde el archivo Front/app.py.
RAIZ = Path(__file__).resolve().parent.parent
# Permitimos importar el módulo Motor desde esa carpeta.
sys.path.insert(0, str(RAIZ))
# Importamos el planeador y la nueva función que entrega las paradas del recorrido.
from motor.viajes import IndiceViajes, cargar_estaciones, cargar_rutas, buscar_mejor_viaje, detalle_recorrido
# Importamos la descarga y el cruce de capas geográficas, exclusivamente desde Front.
from Front.geografia import cargar_capas, preparar_estaciones, normalizar

# Configuramos título y disposición de la pestaña.
st.set_page_config(page_title="RutaViva | TransMilenio", page_icon="🚌", layout="wide", initial_sidebar_state="collapsed")

# Convertimos la ilustración original a una cadena para integrarla sin internet.
imagen_base64 = base64.b64encode((RAIZ / "Assets" / "ciudad.svg").read_bytes()).decode("ascii")

# Definimos una paleta clara y conservamos el encabezado ilustrado.
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');
html,body,[class*="css"],.stApp {{ font-family:'DM Sans',sans-serif; }}
.stApp {{ color:#1e2834;background:linear-gradient(155deg,#fff9f9 0%,#ffffff 45%,#f5f7fa 100%); }}
.block-container {{ max-width:1260px;padding-top:1.3rem; }}
header[data-testid="stHeader"] {{ background:transparent; }}
.hero {{ position:relative;min-height:265px;padding:30px 36px;border-radius:24px;overflow:hidden;margin-bottom:21px;background:linear-gradient(90deg,rgba(32,39,52,.94),rgba(32,39,52,.82) 45%,rgba(32,39,52,.18)),url('data:image/svg+xml;base64,{imagen_base64}') center right/cover no-repeat;box-shadow:0 15px 32px #26354b20; }}
.eyebrow {{ color:#ffdfe0;font-weight:800;letter-spacing:.12em;font-size:12px;margin:9px 0; }}
.hero h1 {{ color:white;font-family:Outfit,sans-serif;font-size:clamp(34px,4vw,58px);line-height:1.1;margin:4px 0 12px; }}
.hero h1 em {{ color:#ff6a74;font-style:normal; }}
.hero p {{ color:#f1f2f3;font-size:16px;max-width:640px; }}
.official-logo {{ position:absolute;right:28px;top:25px;width:110px;max-height:80px;object-fit:contain;border-radius:10px;background:#fffefeee;padding:7px; }}
.brandline {{ display:flex;align-items:center;gap:10px;color:white;font-weight:800; }}
.brand-square {{ padding:9px;background:#e63845;color:white;border-radius:10px; }}
.pill {{ display:inline-block;color:#fff;border:1px solid #ef9da5;background:#cd3d50b9;border-radius:30px;padding:6px 13px;font-size:12px; }}
.sectionhead {{ font-family:Outfit,sans-serif;font-size:25px;font-weight:800;color:#263445;margin-top:17px; }}
.subtitle {{ color:#526378;margin-bottom:15px; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius:20px; }}
[data-testid="stSelectbox"] label,[data-testid="stRadio"] label {{ color:#2a3645!important;font-weight:700; }}
div[data-baseweb="select"]>div {{ background:white;border:1px solid #d9e1e8;border-radius:12px;min-height:48px; }}
div[data-testid="stRadio"] {{ background:#fff;border:1px solid #e0e5eb;border-radius:14px;padding:13px 16px 3px; }}
.stButton>button {{ background:linear-gradient(105deg,#e53446,#c81e33);color:white;border:0;border-radius:12px;font-weight:800;padding:.65rem 1.2rem; }}
.stButton>button:hover {{ background:#b91e30;color:white; }}
div[data-testid="stMetric"] {{ background:white;border:1px solid #e2e6ed;border-radius:14px;padding:12px 16px; }}
div[data-testid="stMetricValue"] {{ color:#243247; }}
.credit {{ border-radius:12px;padding:14px 16px;background:#fff;border:1px solid #e1e6ed;color:#697887;margin-top:24px;font-size:12px; }}
</style>
""",unsafe_allow_html=True)

# Leemos los datos y creamos índices una sola vez por ejecución del servidor.
# Guardamos en memoria cada red para no cargarla repetidamente.
@st.cache_resource
def preparar_red(nombre_carpeta):

    # Construimos la ruta de la carpeta seleccionada.
    carpeta = str(RAIZ / nombre_carpeta)

    # Cargamos las estaciones del archivo CSV.
    estaciones = cargar_estaciones(carpeta)

    # Cargamos los servicios y sus recorridos.
    rutas = cargar_rutas(carpeta)

    # Construimos el índice para buscar viajes rápidamente.
    indice = IndiceViajes(rutas, estaciones)

    # Devolvemos los datos necesarios para el planeador.
    return estaciones, rutas, indice

# Construimos el mapa visual del recorrido ya calculado por el motor.
def mapa_esquematico(detalle):
    # Si no hay detalle de paradas, avisamos sin inventar datos.
    if not detalle:
        # Informamos que falta la secuencia exacta del itinerario.
        st.info("No fue posible reconstruir la secuencia de estaciones.")
        # Terminamos esta función visual.
        return
    # Elegimos un color diferente para cada servicio del viaje.
    colores = ["#fc5261", "#44c6c6"]
    # Obtenemos la cantidad máxima de estaciones en un servicio.
    mayor = 0
    # Recorremos los tramos que entrega el motor.
    for tramo in detalle:
        # Actualizamos el máximo cuando corresponde.
        if len(tramo[1]) > mayor:
            # Guardamos el nuevo máximo.
            mayor = len(tramo[1])
    # Definimos un ancho que deja ver nombres y permite desplazarse.
    ancho = 170 + 170 * (mayor - 1)
    # Dejamos espacio vertical para uno o dos servicios.
    alto = 180 if len(detalle) == 1 else 325
    # Comenzamos un gráfico SVG; este esquema no usa coordenadas geográficas.
    partes = [f'<svg width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" xmlns="http://www.w3.org/2000/svg">']
    # Dibujamos un tramo horizontal para cada servicio seleccionado.
    for num, tramo in enumerate(detalle):
        # Descomponemos el identificador y las estaciones del servicio.
        servicio, paradas = tramo[0], tramo[1]
        # Calculamos la altura de esta fila dentro del esquema.
        y = 78 + num * 145
        # Elegimos su color según el servicio.
        color = colores[num % len(colores)]
        # Dibujamos la línea sobre la cual aparecerán las estaciones.
        fin = 70 + 170 * (len(paradas) - 1)
        # Añadimos esa línea al gráfico.
        partes.append(f'<line x1="70" y1="{y}" x2="{fin}" y2="{y}" stroke="{color}" stroke-width="9" stroke-linecap="round"/>')
        # Mostramos el identificador como encabezado del tramo.
        partes.append(f'<text x="70" y="{y-46}" fill="{color}" font-size="16" font-weight="700">SERVICIO {html.escape(str(servicio))}</text>')
        # Dibujamos las estaciones de esta ruta en el orden recibido.
        for i, nombre in enumerate(paradas):
            # Posicionamos las estaciones a intervalos iguales: no son distancias reales.
            x = 70 + i * 170
            # Los extremos y puntos de transbordo tienen un marcador distinto.
            especial = i == 0 or i == len(paradas) - 1
            # Dibujamos el círculo que representa cada parada.
            partes.append(f'<circle cx="{x}" cy="{y}" r="{13 if especial else 9}" fill="{color if especial else "#202d3b"}" stroke="{color}" stroke-width="4"/>')
            # Dividimos etiquetas largas en dos líneas para que se lean mejor.
            palabras = str(nombre).split(" ")
            # Creamos fragmentos de texto de hasta 18 caracteres.
            lineas = []
            # Empezamos con una línea de texto vacía.
            actual = ""
            # Agregamos palabra por palabra a la etiqueta.
            for palabra in palabras:
                # Si la siguiente palabra cabe en la línea, la añadimos.
                if len(actual) + len(palabra) + 1 <= 18:
                    actual = (actual + " " + palabra).strip()
                # Si no cabe, terminamos esta línea y empezamos otra.
                else:
                    if actual:
                        lineas.append(actual)
                    actual = palabra
            # Incluimos la última línea de texto.
            if actual:
                lineas.append(actual)
            # Limitamos cada etiqueta a tres líneas para mantener la legibilidad.
            for n, linea in enumerate(lineas[:3]):
                # Colocamos las etiquetas debajo de cada parada.
                partes.append(f'<text x="{x}" y="{y+31+n*16}" text-anchor="middle" fill="#e5ecf4" font-size="12" font-weight="600">{html.escape(linea)}</text>')
    # Cerramos el documento SVG.
    partes.append('</svg>')
    # Preparamos la tarjeta desplazable con fondo cuadriculado de mapa.
    contenido = ''.join(partes)
    # Incrustamos el mapa dentro de un panel horizontal con scroll si hace falta.
    components.html(f'''<html><body style="margin:0;background:#172232;color:white;font-family:Arial,sans-serif;"><div style="border:1px solid #405164;border-radius:18px;overflow-x:auto; padding:10px;background-color:#1d2a3a;background-image:linear-gradient(#ffffff06 1px,transparent 1px),linear-gradient(90deg,#ffffff06 1px,transparent 1px);background-size:24px 24px;">{contenido}</div><p style="color:#9baaba;font-size:12px;margin:8px 0 0 5px;">↔ Desliza para ver todas las estaciones · Esquema del orden de paradas, no un mapa geográfico.</p></body></html>''', height=alto+83, scrolling=False)

# Mostramos el resumen y la visualización de un viaje específico.
def mostrar_viaje(resultado, titulo, rutas, indice, origen, destino, cerradas, clave):
    # Escribimos el título del panel de resultado.
    st.markdown(f'<div class="sectionhead">{html.escape(titulo)}</div>', unsafe_allow_html=True)
    # Comprobamos si el motor no encontró alternativas.
    if resultado is None:
        st.warning("No encontramos un viaje válido con máximo un transbordo.")
        return
    # Mostramos las validaciones del motor cuando hay datos incorrectos.
    if resultado[0] == "ERROR":
        st.error(resultado[1])
        return
    # Cuando origen y destino coinciden, no es necesario tomar un bus.
    if resultado[0] == "MISMO DESTINO":
        st.success("¡Ya estás en tu destino! No necesitas abordar un bus.")
        return
    # Informamos la cantidad de cambios según el resultado del motor.
    cambios = 1 if resultado[0] == "TRANSBORDO" else 0
    # Mostramos dos métricas resumidas en columnas.
    a, b = st.columns(2)
    # La primera métrica indica el número de tramos entre estaciones.
    a.metric("🚏 Tramos", resultado[4])
    # La segunda informa los cambios de servicio.
    b.metric("🔄 Transbordos", cambios)
    # Mostramos el primer servicio que se debe tomar.
    st.markdown(f'**🚌 Toma el servicio:** `{html.escape(str(resultado[1]))}`')
    # Si hay transbordo, explicamos dónde ocurre y qué servicio sigue.
    if cambios:
        st.markdown(f'**🔁 Cambia en:** {html.escape(str(resultado[3]))} → **Servicio** `{html.escape(str(resultado[2]))}`')
    # Si es directo, el pasajero no necesita cambiar de bus.
    else:
        st.markdown('**✅ Sin transbordos:** permanece en el mismo servicio.')
    # Solicitamos al motor las paradas exactas de cada tramo elegido.
    detalle = detalle_recorrido(rutas, indice, resultado, origen, destino, cerradas)
    # Mostramos el esquema cuando hay un itinerario válido.
    if detalle:
        # Añadimos una cabecera para el mapa del viaje.
        st.markdown('**🗺️ Tu recorrido, estación por estación**')
        # Pintamos la ruta visual mediante SVG.
        mapa_esquematico(detalle)
        # Creamos un resumen textual útil para accesibilidad y sustentación.
        with st.expander("📋 Ver instrucciones paso a paso", expanded=False):
            # El primer paso empieza en el origen.
            st.write(f"**1.** Sube al servicio **{detalle[0][0]}** en **{origen}**.")
            # Si hay segundo tramo, identificamos el transbordo.
            if len(detalle) == 2:
                st.write(f"**2.** Baja en **{resultado[3]}** y cambia al servicio **{detalle[1][0]}**.")
                st.write(f"**3.** Baja en **{destino}**.")
            # En viaje directo basta con bajarse en el destino.
            else:
                st.write(f"**2.** Baja en **{destino}**.")
            # Enumeramos las paradas de cada servicio sin alterar el algoritmo.
            for tramo in detalle:
                # Etiquetamos el servicio y su secuencia real de estaciones.
                st.write(f"**Servicio {tramo[0]}:** " + " → ".join(tramo[1]))

# Dibujamos la cabecera visual con ilustración de Bogotá y marca académica.
st.markdown('''<section class="hero"><img class="official-logo" src="https://commons.wikimedia.org/wiki/Special:FilePath/TransMilenio%20S.%20A.%20Bogot%C3%A1%20logo.svg" alt="Logotipo institucional de TransMilenio"/><div class="brandline"><span class="brand-square">TM</span><span>RUTAVIVA · PLANIFICADOR</span></div><div class="eyebrow">MUÉVETE MEJOR POR BOGOTÁ</div><h1>Tu ciudad.<br><em>Tu mejor ruta.</em></h1><p>Encuentra conexiones entre estaciones, compara opciones y descubre dónde hacer transbordo.</p><span class="pill">🚌 Datos históricos · Red académica TransMilenio</span></section>''', unsafe_allow_html=True)

# Mostramos una cabecera de búsqueda, fuera de la lógica de rutas.
st.markdown('<div class="sectionhead">Planea tu próximo recorrido</div>', unsafe_allow_html=True)
# Explicamos al usuario qué debe seleccionar.
st.markdown('<div class="subtitle">Elige tu origen, destino y cómo quieres viajar.</div>', unsafe_allow_html=True)

# Cargamos los datos e índices que utiliza el motor.
# Permitimos seleccionar la fuente de información.
fuente = st.selectbox(
    "🗂️ ¿Qué datos quieres utilizar?",
    [
        "Datos académicos del profesor (2021)",
        "Datos GTFS convertidos (2026)"
    ]
)

# Identificamos la carpeta correspondiente.
if fuente == "Datos académicos del profesor (2021)":
    nombre_carpeta = "Datos"
else:
    nombre_carpeta = "Datos_corregidos"

# Cargamos las estaciones, rutas e índice de la fuente seleccionada.
estaciones, rutas, indice = preparar_red(nombre_carpeta)
# Conservamos una lista de cierres provisional para la demostración.
cerradas = ["CALLE 57"]

# Situamos ambos selectores lado a lado.
col1, col2 = st.columns(2, gap="medium")
# Presentamos la selección de origen en la columna izquierda.
with col1:
    origen = st.selectbox("📍 Estación de origen", estaciones)
# Presentamos la selección de destino en la columna derecha.
with col2:
    destino = st.selectbox("🏁 Estación de destino", estaciones, index=1 if len(estaciones) > 1 else 0)

# Ofrecemos el criterio oficial R5 y la opción adicional de preferir menos cambios.
modo = st.radio("¿Qué prefieres?", ["Menos paradas", "Menos transbordos", "Comparar ambas"], horizontal=True)
# Explicamos que el cierre actual es de demostración.
st.caption("Datos históricos para demostración · CALLE 57 está cerrada solo en esta simulación.")
# Preparamos el viaje que se destacará geográficamente en el mapa.
resultado_mapa = None
# Ejecutamos la consulta solamente cuando el usuario presiona el botón.
if st.button("🔎 Encontrar mi ruta", type="primary", use_container_width=True):
    # Para comparar las opciones buscamos con los dos criterios del motor.
    if modo == "Comparar ambas":
        # Buscamos la alternativa exigida oficialmente: menos paradas.
        resultado_paradas = buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice, "paradas")
        # Destacaremos la alternativa oficial de menos paradas en el mapa.
        resultado_mapa = resultado_paradas
        # Buscamos la alternativa adicional con la menor cantidad de transbordos.
        resultado_cambios = buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice, "transbordos")
        # Mostramos los resultados uno debajo del otro para que el mapa sea legible.
        mostrar_viaje(resultado_paradas, "🏆 Opción 1 · Menos paradas", rutas, indice, origen, destino, cerradas, "p")
        st.divider()
        mostrar_viaje(resultado_cambios, "🔁 Opción 2 · Menos transbordos", rutas, indice, origen, destino, cerradas, "t")
    # Cuando se elige un solo criterio mostramos el viaje correspondiente.
    else:
        # Traducimos la opción elegida al identificador de criterio del motor.
        criterio = "paradas" if modo == "Menos paradas" else "transbordos"
        # Solicitamos el viaje al motor sin calcularlo desde el front.
        resultado = buscar_mejor_viaje(rutas, estaciones, cerradas, origen, destino, indice, criterio)
        # Guardamos la alternativa elegida para mostrar sus estaciones en el mapa.
        resultado_mapa = resultado
        # Dibujamos el resultado y su recorrido estación por estación.
        mostrar_viaje(resultado, "🗺️ Recorrido recomendado", rutas, indice, origen, destino, cerradas, "u")

# Mostramos el aviso final y la referencia al logo institucional disponible online.
st.markdown('<div class="credit">Proyecto académico independiente · Datos históricos, no información en tiempo real · El esquema muestra el orden de paradas, NO su ubicación física ni distancias. Para un mapa geográfico se requieren coordenadas verificadas de cada estación.</div>', unsafe_allow_html=True)



# -------------------------------------------------------------
# MAPA OFICIAL INTERACTIVO — CAPA DEL FRONT, NO DEL MOTOR R5
# -------------------------------------------------------------
# Importamos JSON para pasar la información de estaciones y vías a Leaflet.
import json

# Este caché evita consultar constantemente los servidores oficiales.
@st.cache_data(ttl=3600, show_spinner=False)
def obtener_mapa_oficial(actualizar=False):
    # Descargamos o recuperamos las últimas capas geográficas disponibles.
    return cargar_capas(RAIZ / 'Datos', actualizar)

# Dibujamos estaciones y vías oficiales; el algoritmo sigue en Motor/viajes.py.
def pintar_mapa(puntos, troncales, servicios, seleccion, origen, destino, transbordo):
    # Convertimos estaciones validadas a JSON para JavaScript.
    puntos_json = json.dumps(puntos,ensure_ascii=False)
    # Convertimos corredores geográficos a GeoJSON sin recalcular viajes.
    troncales_json = json.dumps(troncales,ensure_ascii=False)
    # Convertimos las listas de servicios históricos a JSON.
    servicios_json = json.dumps(servicios,ensure_ascii=False)
    # Convertimos el recorrido elegido en una lista de nombres para resaltarlo.
    seleccion_json = json.dumps(seleccion,ensure_ascii=False)
    # Guardamos el origen, destino y transbordo como texto seguro en JSON.
    focos_json = json.dumps({'origen':origen,'destino':destino,'transbordo':transbordo},ensure_ascii=False)
    # Creamos el HTML del mapa dentro de la interfaz, sin modificar el motor.
    html_mapa = r'''<!DOCTYPE html><html lang="es"><head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <style>
      *{box-sizing:border-box}html,body{margin:0;background:#fff;font-family:Arial,Helvetica,sans-serif;color:#263445}
      #map{height:490px;width:100%;border-radius:18px;overflow:hidden;background:#eef1f5}
      #info{margin-top:12px;padding:14px 18px;min-height:56px;border:1px solid #e5e9f0;border-radius:14px;background:#fff;color:#334155;font-size:14px;line-height:1.55}
      .legenda{display:flex;gap:18px;flex-wrap:wrap;margin:10px 0 0 3px;color:#64748b;font-size:12px}
      .bolita{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:middle;margin-right:5px}
      .leaflet-popup-content{margin:0!important;line-height:1.5;font-size:13px}
      .leaflet-popup-content-wrapper{border-radius:17px;padding:0;box-shadow:0 12px 35px #10182825;overflow:hidden}
      .leaflet-popup-content{min-width:245px;max-width:315px}
      .leaflet-container{font-family:Arial,sans-serif}
      .rv-card{padding:17px 18px 16px;color:#263445;background:#fff}
      .rv-card .rv-kicker{color:#d93649;font-size:10px;letter-spacing:.1em;text-transform:uppercase;font-weight:800;margin-bottom:5px}
      .rv-card .rv-name{font-size:18px;font-weight:800;line-height:1.22;color:#182331;margin-bottom:9px}
      .rv-card .rv-address{font-size:12px;color:#64748b;line-height:1.45;margin-bottom:13px}
      .rv-card .rv-section{font-size:12px;color:#334155;font-weight:750;margin-bottom:7px}
      .rv-card .rv-badges{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px}
      .rv-card .rv-badge{background:#fff0f1;border:1px solid #fbd5da;border-radius:7px;padding:3px 7px;color:#a92337;font-size:11px;font-weight:750}
      .rv-card .rv-note{font-size:10px;color:#8190a2;line-height:1.4;margin:8px 0 0}
      .rv-card .rv-details{border-top:1px solid #edf0f4;margin-top:11px;padding-top:9px}
      .rv-card .rv-details summary{font-size:11px;color:#64748b;cursor:pointer;font-weight:650}
      .rv-card .rv-details div{font-size:11px;color:#475569;margin-top:7px;word-break:break-word}
      .rv-card .rv-status{background:#e8f7f0;color:#18744e;display:inline-block;font-size:11px;padding:4px 8px;border-radius:999px;margin:3px 5px 5px 0;font-weight:750}
      .rv-card .rv-muted{color:#64748b;font-size:12px}
    </style></head><body>
    <div id="map"></div><div class="legenda"><span><i class="bolita" style="background:#e63946"></i>Estación del recorrido</span><span><i class="bolita" style="background:#0891b2"></i>Estación de transbordo</span><span><i class="bolita" style="background:#78889b"></i>Otras estaciones</span><span>━ Corredores geográficos oficiales</span></div>
    <div id="info">🚏 Selecciona una estación o una línea troncal para conocer sus datos.</div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script>
    const estaciones=__PUNTOS__, troncales=__TRONCALES__, servicios=__SERVICIOS__, seleccion=__SELECCION__, focos=__FOCOS__;
    const mapa=L.map('map',{preferCanvas:true}).setView([4.653,-74.094],11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors',maxZoom:18}).addTo(mapa);
    const caja=document.getElementById('info');
    function escapar(v){return String(v===undefined?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
    function dato(prop,nombre){const encontrado=Object.keys(prop||{}).find(k=>k.toLowerCase()===nombre.toLowerCase());return encontrado?prop[encontrado]:'';}
    const estacionesElegidas=new Set(seleccion); let tramosMarcados=[];
    // Dibujamos los corredores oficiales como infraestructura, NO como recorrido de un bus específico.
    if(troncales.features && troncales.features.length){
      L.geoJSON(troncales,{style:()=>({color:'#b84252',weight:3,opacity:.55}),onEachFeature:(f,capa)=>{
        const p=f.properties||{}, troncal=dato(p,'nom_tronc')||'Troncal', trazado=dato(p,'nom_traz')||'Tramo';
        const mensaje='<strong>🛣️ '+escapar(troncal)+'</strong><br>Tramo: '+escapar(trazado)+'<br><small>Infraestructura geográfica; no confirma servicios en tiempo real.</small>';
        capa.bindPopup(mensaje);
        capa.on('click',()=>{caja.innerHTML=mensaje;});
        capa.on('mouseover',()=>{capa.setStyle({weight:6,opacity:.95});});
        capa.on('mouseout',()=>{capa.setStyle({weight:3,opacity:.55});});
      }}).addTo(mapa);
    }
    // Recorremos cada estación oficial y relacionamos únicamente coincidencias verificadas con 2021.
    for(const p of estaciones){
      const clave=p.historico||'';
      const incluida=estacionesElegidas.has(clave);
      const esCambio=clave && clave===focos.transbordo;
      const esOrigen=clave && clave===focos.origen;
      const esDestino=clave && clave===focos.destino;
      const color=esCambio?'#0891b2':incluida?'#e63946':'#78889b';
      const radio=esCambio?10:(incluida?8:4);
      const marcador=L.circleMarker([p.lat,p.lon],{radius:radio,color:'#ffffff',weight:1.5,fillColor:color,fillOpacity:.93});
      marcador.addTo(mapa);
      // Los identificadores son útiles, pero los presentamos como etiquetas legibles.
      const lista=(servicios[clave]||[]);
      const etiquetas=lista.slice(0,10).map(codigo=>'<span class="rv-badge">'+escapar(codigo)+'</span>').join('');
      const extra=lista.length>10?'<span class="rv-badge">+'+(lista.length-10)+' más</span>':'';
      // Ventana con jerarquía visual, en lugar de un párrafo técnico de códigos.
      let texto='<div class="rv-card"><div class="rv-kicker">🚏 Estación TransMilenio</div>';
      texto+='<div class="rv-name">'+escapar(p.nombre)+'</div>';
      if(p.ubicacion){texto+='<div class="rv-address">📍 '+escapar(p.ubicacion)+'</div>';}
      if(esOrigen)texto+='<span class="rv-status">🟢 Tu origen</span>';
      if(esDestino)texto+='<span class="rv-status">🏁 Tu destino</span>';
      if(esCambio)texto+='<span class="rv-status">🔄 Transbordo</span>';
      if(incluida && !esOrigen && !esDestino && !esCambio)texto+='<span class="rv-status">✓ En tu recorrido</span>';
      if(clave && lista.length){
        texto+='<div class="rv-section">🚌 Servicios asociados <span class="rv-muted">('+lista.length+')</span></div>';
        texto+='<div class="rv-badges">'+etiquetas+extra+'</div>';
        texto+='<div class="rv-note">Servicios del conjunto de datos seleccionado. Información de referencia; no garantiza operación actual.</div>';      }else if(clave){
        texto+='<div class="rv-muted">No hay servicios asociados en el conjunto de datos seleccionado.</div>';
      }else{
       texto+='<div class="rv-muted">Esta estación no tiene una coincidencia confirmada en el conjunto de datos seleccionado.</div>';
      }
      if(clave){texto+='<details class="rv-details"><summary>Ver referencia del conjunto de datos</summary><div>'+escapar(clave)+' · 2021</div></details>';}
      texto+='</div>';
      marcador.bindPopup(texto,{maxWidth:335});
      marcador.on('click',()=>{caja.innerHTML=texto;});
      if(incluida){tramosMarcados.push([p.lat,p.lon]);}
    }
    // Ajustamos el mapa para hacer visibles las estaciones resaltadas, si hay coincidencias geográficas.
    if(tramosMarcados.length){mapa.fitBounds(L.latLngBounds(tramosMarcados).pad(.23),{maxZoom:14});}
    // No dibujamos líneas rectas como si fueran las vías del servicio. Las vías dibujadas sí son oficiales.
    if(!estaciones.length && !((troncales.features||[]).length)){
       caja.textContent='🗺️ Mapa de Bogotá disponible. Las capas de estaciones y corredores se cargarán cuando el servidor de datos permita la conexión.';
    }
    </script></body></html>'''
    # Reemplazamos cada marcador de datos con un JSON generado por Python.
    html_mapa = html_mapa.replace('__PUNTOS__',puntos_json).replace('__TRONCALES__',troncales_json)
    html_mapa = html_mapa.replace('__SERVICIOS__',servicios_json).replace('__SELECCION__',seleccion_json).replace('__FOCOS__',focos_json)
    # Mostramos un mapa interactivo con sus controles de zoom y puntos seleccionables.
    components.html(html_mapa,height=615,scrolling=False)

# Separamos la visualización geográfica del cálculo de rutas del motor.
st.markdown('<div class="sectionhead">🗺️ Explora las estaciones y troncales</div>',unsafe_allow_html=True)
# Permitimos actualizar la copia de las capas solo cuando el usuario lo solicite.
col_mapa, col_accion = st.columns([4,1],vertical_alignment='center')
# Presentamos una explicación breve de cómo interactuar con la cartografía.
with col_mapa:
    st.caption('Toca una estación o una línea roja para consultar sus datos y explorar Bogotá.')
# Ofrecemos una opción discreta para actualizar las capas públicas.
with col_accion:
    actualizar_mapa = st.button('↻ Actualizar mapa',use_container_width=True)
# Si se solicitó actualizar, limpiamos la copia de Streamlit y cargamos los datos de nuevo.
if actualizar_mapa:
    obtener_mapa_oficial.clear()
# Leemos las capas públicas, con copia local si ya se descargaron.
estaciones_geo, troncales_geo = obtener_mapa_oficial(actualizar_mapa)
# Comprobamos coincidencias normalizadas de nombres de estaciones con los CSV académicos.
puntos = preparar_estaciones(estaciones_geo, estaciones)
# Construimos un índice de servicios informativo: NO se utiliza para calcular rutas.
servicios_por_estacion = {}
# Recorremos las rutas históricas cargadas por el motor.
for ruta in rutas:
    # Leemos el identificador de esta ruta.
    servicio = ruta[0]
    # Recorremos las paradas registradas para este servicio.
    for parada in ruta[1]:
        # Extraemos el nombre de la estación histórica.
        nombre = parada[1]
        # Creamos su listado si todavía no existe.
        if nombre not in servicios_por_estacion:
            servicios_por_estacion[nombre] = []
        # Evitamos duplicar el mismo servicio en la información visual.
        if servicio not in servicios_por_estacion[nombre]:
            servicios_por_estacion[nombre].append(servicio)

# Prepararemos los nombres del recorrido seleccionado, si existe una consulta válida.
nombres_recorrido = []
# Comenzamos sin estación de cambio, porque puede tratarse de un viaje directo.
transbordo_seleccionado = ''
# Confirmamos que hay un resultado válido de los cálculos del motor.
if resultado_mapa is not None and resultado_mapa[0] not in ('ERROR','MISMO DESTINO'):
    # Le pedimos al motor su lista de estaciones, sin recalcular el itinerario en el front.
    detalles_mapa = detalle_recorrido(rutas, indice, resultado_mapa, origen, destino, cerradas)
    # Recorremos los servicios del viaje calculado.
    for tramo in detalles_mapa:
        # Recorremos todas las estaciones de ese servicio.
        for nombre in tramo[1]:
            # Evitamos repetir nombres dentro de la selección.
            if nombre not in nombres_recorrido:
                nombres_recorrido.append(nombre)
    # Leemos la estación de transbordo solo cuando el resultado lo requiere.
    if resultado_mapa[0] == 'TRANSBORDO':
        transbordo_seleccionado = resultado_mapa[3]

# Mostramos las estaciones oficiales y los corredores públicos sobre OpenStreetMap.
pintar_mapa(puntos, troncales_geo, servicios_por_estacion, nombres_recorrido,
            origen if nombres_recorrido else '', destino if nombres_recorrido else '', transbordo_seleccionado)
# Aclaramos la diferencia de fechas con una nota discreta, sin alertas técnicas azules.
st.caption('Mapa geográfico oficial: consulta de estaciones y troncales. Servicios y viajes: CSV académico histórico de 2021. No son datos en tiempo real.')
# Cerramos la página con una nota de crédito y alcance clara.
st.markdown('<div class="credit">RutaViva · Planeador independiente. Ubicaciones y trazados: TransMilenio / Datos Abiertos Bogotá (CC BY 4.0). Mapa base © OpenStreetMap. Los tramos geográficos no prueban el recorrido exacto de cada servicio histórico.</div>',unsafe_allow_html=True)