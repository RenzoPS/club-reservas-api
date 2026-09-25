"""Configuracion de la aplicacion y reglas de dominio."""
import os
from datetime import timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------
# API
# ---------------------------------------------------------------
BASE_URL = '/club_reservas_api'

# ---------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', '3306'))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
DB_NAME     = os.getenv('DB_NAME', 'club')
DB_URL      = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# ---------------------------------------------------------------
# Fechas y horarios
# ---------------------------------------------------------------
# Todo se interpreta en GMT-3, sin conversion de zona horaria.
TZ_ARG = timezone(timedelta(hours=-3))
OFFSET_ESPERADO = '-03:00'

# 2026-10-15T18:00:00.000000-03:00
FORMATO_FECHA_HORA = '%Y-%m-%dT%H:%M:%S.%f%z'
FORMATO_FECHA      = '%Y-%m-%d'
FORMATO_HORA       = '%H:%M'

HORA_APERTURA = 8
HORA_CIERRE   = 23

DURACION_MIN_HORAS = 1
DURACION_MAX_HORAS = 3

# ---------------------------------------------------------------
# Paginacion
# ---------------------------------------------------------------
LIMIT_DEFAULT  = 10
LIMIT_MIN      = 1
LIMIT_MAX      = 100
OFFSET_DEFAULT = 0

# ---------------------------------------------------------------
# Estados de reserva
# ---------------------------------------------------------------
ESTADO_CONFIRMADA = 'confirmada'
ESTADO_CANCELADA  = 'cancelada'
ESTADO_FINALIZADA = 'finalizada'

ESTADOS_VALIDOS = (ESTADO_CONFIRMADA, ESTADO_CANCELADA, ESTADO_FINALIZADA)

# ---------------------------------------------------------------
# Codigos de error
# ---------------------------------------------------------------
ERROR_CODE_INVALID_BODY       = 'invalid.body'
ERROR_CODE_INVALID_FORMAT     = 'invalid.format'
ERROR_CODE_INVALID_MIN_VALUE  = 'invalid.min.value'
ERROR_CODE_INVALID_MAX_VALUE  = 'invalid.max.value'
ERROR_CODE_UNKNOWN_FIELD      = 'unknown.field'

ERROR_CODE_DEPORTE_NOT_FOUND  = 'deporte.not.found'
ERROR_CODE_CANCHA_NOT_FOUND   = 'cancha.not.found'
ERROR_CODE_SOCIO_NOT_FOUND    = 'socio.not.found'
ERROR_CODE_RESERVA_NOT_FOUND  = 'reserva.not.found'

ERROR_CODE_EMAIL_DUPLICADO      = 'socio.email.duplicado'
ERROR_CODE_CANCHA_CON_RESERVAS  = 'cancha.con.reservas'
ERROR_CODE_CANCHA_INACTIVA      = 'cancha.inactiva'
ERROR_CODE_SOCIO_INACTIVO       = 'socio.inactivo'
ERROR_CODE_SUPERPOSICION_CANCHA = 'reserva.superpuesta.cancha'
ERROR_CODE_SUPERPOSICION_SOCIO  = 'reserva.superpuesta.socio'
ERROR_CODE_TRANSICION_INVALIDA  = 'reserva.transicion.invalida'
