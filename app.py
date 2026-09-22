"""Punto de entrada de la API.

    source venv/bin/activate
    python app.py

Disponible en http://localhost:5000/club_reservas_api
"""
import logging

from flask import Flask

from club_reservas.constants import BASE_URL

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__)
app.json.sort_keys = False

# Cada recurso se agrupa en un Blueprint y se registra aca:
#
#     from club_reservas.routes.canchas import canchas_bp
#     app.register_blueprint(canchas_bp, url_prefix=BASE_URL)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
