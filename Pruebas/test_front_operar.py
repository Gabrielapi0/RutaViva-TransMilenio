"""Prueba rapida del Blueprint (requiere Flask)."""
import os
import sys
from _red_prueba import red_mini

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Front"))
from flask import Flask  # noqa: E402
from operar_red import crear_blueprint  # noqa: E402


def test_flujo():
    red = red_mini()
    app = Flask(__name__)
    app.register_blueprint(crear_blueprint(red))
    c = app.test_client()
    assert c.get("/operar/").status_code == 200
    assert c.post("/operar/api/cerrar", json={"nombre": "GAMMA"}).get_json()["ok"] is True
    assert c.post("/operar/api/cerrar", json={"nombre": "GAMMA"}).get_json()["ok"] is False
    assert c.get("/operar/api/recorrido?ruta=RUTA_A&al_reves=true").get_json()["paradas"][0] == "GAMMA"
    assert c.post("/operar/api/deshacer", json={}).get_json()["cerradas"] == []
    assert c.post("/operar/api/rehacer", json={}).get_json()["cerradas"] == ["GAMMA"]


if __name__ == "__main__":
    test_flujo()
    print("OK test_flujo")
