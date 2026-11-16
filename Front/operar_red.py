"""Pantalla "Operar la red": editar rutas, cerrar/reabrir, deshacer/rehacer.

Es un Blueprint de Flask. En Front/app.py (de la Integrante 3) basta con:

    from operar_red import crear_blueprint
    app.register_blueprint(crear_blueprint(red))      # red = instancia de Red

Si el front usa otro framework, la logica es solo llamar a los metodos de red.
Aqui se puede usar cualquier libreria (esto NO es motor/).
"""
from flask import Blueprint, jsonify, request, Response

PAGINA = """<!doctype html><html lang="es"><meta charset="utf-8">
<title>Operar la red</title>
<style>
body{font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem}
fieldset{margin:1rem 0;border-radius:8px}input,button{padding:.4rem;margin:.2rem}
#msg{padding:.6rem;background:#eef;border-radius:6px;min-height:1.2rem}
li{list-style:none}
</style>
<h1>Operar la red</h1><div id="msg"></div>
<fieldset><legend>Recorrido (R7)</legend>
<input id="r" placeholder="Ruta, ej. 1-1"><label><input type="checkbox" id="rev"> al reves</label>
<button onclick="ver()">Ver</button><ol id="lista"></ol></fieldset>
<fieldset><legend>Editar ruta (R7)</legend>
<input id="er" placeholder="Ruta"><input id="en" placeholder="Estacion nueva / a quitar">
<input id="ed" placeholder="Despues de (solo agregar)">
<button onclick="op('agregar',{ruta:er.value,nueva:en.value,despues_de:ed.value})">Agregar parada</button>
<button onclick="op('quitar',{ruta:er.value,estacion:en.value})">Quitar parada</button></fieldset>
<fieldset><legend>Cerrar / reabrir (R8)</legend>
<input id="c" placeholder="Estacion">
<button onclick="op('cerrar',{nombre:c.value})">Cerrar</button>
<button onclick="op('reabrir',{nombre:c.value})">Reabrir</button>
<p>Cerradas: <span id="cer"></span></p></fieldset>
<fieldset><legend>Historial (R9)</legend>
<button onclick="op('deshacer',{})">Deshacer</button>
<button onclick="op('rehacer',{})">Rehacer</button></fieldset>
<script>
const base=location.pathname.replace(/\\/$/,'');
async function op(n,d){const r=await fetch(base+'/api/'+n,{method:'POST',
 headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
 const j=await r.json();msg.textContent=j.mensaje;cer.textContent=j.cerradas.join(', ')||'(ninguna)';
 if(document.getElementById('r').value) ver();}
async function ver(){const q=new URLSearchParams({ruta:r.value,al_reves:rev.checked});
 const j=await (await fetch(base+'/api/recorrido?'+q)).json();
 lista.innerHTML=j.paradas.map(p=>'<li>'+p+'</li>').join('');
 if(!j.paradas.length) msg.textContent='Ruta inexistente';}
op('estado',{});
</script></html>"""


def crear_blueprint(red, prefijo="/operar"):
    bp = Blueprint("operar_red", __name__, url_prefix=prefijo)

    def respuesta(ok, bueno, malo):
        return jsonify(ok=ok, mensaje=bueno if ok else malo,
                       cerradas=list(red.cerradas))

    @bp.get("/")
    def pagina():
        return Response(PAGINA, mimetype="text/html")

    @bp.get("/api/recorrido")
    def api_recorrido():
        al_reves = request.args.get("al_reves", "false") == "true"
        return jsonify(paradas=red.recorrido(request.args.get("ruta", ""), al_reves))

    @bp.post("/api/estado")
    def api_estado():
        return respuesta(True, "Listo", "")

    @bp.post("/api/agregar")
    def api_agregar():
        d = request.get_json(force=True)
        return respuesta(red.agregar_parada(d.get("ruta"), d.get("nueva"), d.get("despues_de")),
                         "Parada agregada",
                         "No se pudo agregar (ruta o estacion invalida, repetida o cerrada)")

    @bp.post("/api/quitar")
    def api_quitar():
        d = request.get_json(force=True)
        return respuesta(red.quitar_parada(d.get("ruta"), d.get("estacion")),
                         "Parada quitada", "No se pudo quitar (ruta o parada inexistente)")

    @bp.post("/api/cerrar")
    def api_cerrar():
        d = request.get_json(force=True)
        return respuesta(red.cerrar(d.get("nombre")), "Estacion cerrada",
                         "No se pudo cerrar (no existe o ya estaba cerrada)")

    @bp.post("/api/reabrir")
    def api_reabrir():
        d = request.get_json(force=True)
        return respuesta(red.reabrir(d.get("nombre")), "Estacion reabierta",
                         "No se pudo reabrir (no existe o ya estaba abierta)")

    @bp.post("/api/deshacer")
    def api_deshacer():
        return respuesta(red.deshacer(), "Cambio deshecho", "No hay nada que deshacer")

    @bp.post("/api/rehacer")
    def api_rehacer():
        return respuesta(red.rehacer(), "Cambio rehecho", "No hay nada que rehacer")

    return bp
