"""Configuracion de la aplicacion."""
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = '/club_reservas_api'

DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME     = os.getenv('DB_NAME', 'club')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
