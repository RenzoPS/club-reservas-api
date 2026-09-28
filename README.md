# Club Reservas API

API REST para gestionar canchas, socios y reservas del Club Deportivo Encuentro.

Trabajo practico de Introduccion al Desarrollo de Software (FIUBA).

## Integrantes

| Nombre | Padron |
|--------|--------|
| Ivan Angulo Farias | 107047 |
| Luis Gerardo Zambrano Vera | 97605 |
| Martin Alejandro Campuzano Jorquera | 115327 |
| Renzo Piris Saporito | 116276 |
| Valentina Rivarola | 115957 |

## Versiones utilizadas

| Componente | Version |
|------------|---------|
| Python | 3.14.7 |
| Flask | 3.1.3 |
| SQLAlchemy | 2.0.54 |
| mysql-connector-python | 26.7.0 |
| python-dotenv | 1.2.3 |
| MySQL | 8 (via Docker) |

Las versiones estan fijadas en `requirements.txt` para que el proyecto se
levante igual en cualquier maquina.

## Requisitos previos

- **Python 3.10 o superior.** El codigo usa sintaxis de tipos (`dict | None`) que
  no existe en versiones anteriores. Verificar antes de empezar:

  ```bash
  python3 --version      # Windows: python --version
  ```

- Docker y Docker Compose (o MySQL 8 instalado localmente)

## Instalacion

```bash
git clone <url-del-repo>
cd club-reservas-api

cp .env.example .env
docker compose up -d
```

### Entorno virtual y dependencias

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell o CMD)**

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Cuando el entorno esta activo, el prompt arranca con `(venv)`. Para salir: `deactivate`.

### Si algo falla

| Error | Solucion |
|-------|----------|
| `ensurepip is not available` | Debian/Ubuntu: `sudo apt install python3-venv` |
| `externally-managed-environment` | Estas instalando fuera del venv. Activalo primero |
| `TypeError: unsupported operand type(s) for \|` | Tu Python es menor a 3.10 |
| `source: command not found` | Estas en Windows: usa `venv\Scripts\activate` |

### Base de datos

El contenedor ejecuta `db/init_db.sql` automaticamente **solo la primera vez**,
cuando el volumen de datos se crea vacio. Ahi se crean las tablas y se cargan
los datos iniciales.

La base `club` la crea el propio contenedor (`MYSQL_DATABASE` en el compose),
asi que el script no necesita `CREATE DATABASE` ni `USE`: va directo con los
`CREATE TABLE`.

MySQL tarda unos segundos en quedar listo despues del `up`. Para ver cuando esta:

```bash
docker compose logs -f mysql      # esperar la linea "ready for connections"
```

> **Si modificas `init_db.sql`, el cambio NO se aplica solo.**
>
> El volumen ya tiene datos, asi que el contenedor no vuelve a ejecutar el script.
> Ni `restart` ni `down` alcanzan. Hay que destruir el volumen con `-v`:
>
> ```bash
> docker compose down -v && docker compose up -d
> ```
>
> Esto borra todos los datos de la base y los vuelve a cargar desde el script.

### Datos de prueba

`init_db.sql` crea las tablas y carga los deportes, que son obligatorios. Los
datos ficticios de socios y canchas van en un script aparte, que **no** se
ejecuta con el contenedor: se corre una sola vez, cuando se quieren datos con
los que probar.

**Con Docker**

```bash
docker compose exec -T mysql mysql -uroot -proot club < db/datos_prueba.sql
```

El `-T` desactiva el TTY, sin eso la redireccion no llega al `mysql` del
contenedor.

El script empieza con `SET NAMES utf8mb4`, porque el cliente de linea de comandos
de MySQL asume `latin1` y guardaria corruptos los nombres con acento.

**Sin Docker**

```bash
mysql -u root -p club < db/datos_prueba.sql
```

**Windows PowerShell**

```powershell
Get-Content db\datos_prueba.sql | docker compose exec -T mysql mysql -uroot -proot club
```

Carga 10 socios y 10 canchas con casos variados para ejercitar los filtros:
canchas activas e inactivas, techadas y descubiertas, de los tres deportes, y
socios activos e inactivos.

> **Se corre una sola vez.** Una segunda ejecucion duplica las canchas y falla
> en los socios por el `UNIQUE` del email. Para volver al estado inicial:
>
> ```bash
> docker compose down -v && docker compose up -d
> ```
>
> Eso recrea el esquema y los deportes. Los datos de prueba se vuelven a cargar
> con el comando de arriba.

El script no incluye reservas. El enunciado solo admite reservas con fecha de
inicio futura, y cualquier fecha fija en un script quedaria en el pasado al poco
tiempo, invalidando las pruebas de disponibilidad. Las reservas se crean desde
la API con `POST /reservas`.

### Sin Docker

Si tenes MySQL 8 instalado localmente, el script lo corres a mano:

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS club;"
mysql -u root -p club < db/init_db.sql
```

En Windows PowerShell la segunda linea va asi:

```powershell
Get-Content db\init_db.sql | mysql -u root -p club
```

Aca no hay carga automatica: lo corres vos cada vez que quieras recargar el esquema.
Si cambian los datos de conexion, actualizar el `.env` antes de levantar la API.

## Ejecucion

```bash
source venv/bin/activate
python app.py
```

La API queda en http://localhost:5000/club_reservas_api

## Configuracion

Variables de entorno en `.env` (ver `.env.example`):

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | Host de MySQL |
| `DB_PORT` | `3306` | Puerto de MySQL |
| `DB_USER` | `root` | Usuario |
| `DB_PASSWORD` | `root` | Password |
| `DB_NAME` | `club` | Nombre de la base |

El `.env` no se commitea.

## Estructura

```
app.py                      arranque, registra los blueprints
club_reservas/
  constants.py              configuracion
  repositories/             acceso a datos (SQL)
  routes/                   endpoints HTTP (blueprints de Flask)
  services/                 logica de negocio
  validators/               validacion del input
db/init_db.sql              esquema y datos iniciales
docs/swagger.yaml           contrato de la API
```

## Endpoints

Todos cuelgan del prefijo `/club_reservas_api`. El contrato completo esta en
[`docs/swagger.yaml`](docs/swagger.yaml), que se puede visualizar pegando su
contenido en [editor.swagger.io](https://editor.swagger.io), con la extension
"Swagger Viewer" de VSCode, o con cualquier renderer compatible con OpenAPI 3.

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/deportes` | Listar los deportes precargados. Sin paginacion |
| GET | `/canchas` | Listar canchas. Filtros: `id_deporte`, `nombre`, `techada`, `activa` |
| POST | `/canchas` | Crear una cancha |
| GET | `/canchas/{id}` | Detalle de una cancha |
| PATCH | `/canchas/{id}` | Actualizar parcialmente una cancha |
| DELETE | `/canchas/{id}` | Eliminar una cancha sin reservas asociadas |
| GET | `/canchas/disponibles` | Canchas activas libres durante un intervalo |
| GET | `/socios` | Listar socios. Filtros: `nombre`, `activo` |
| POST | `/socios` | Registrar un socio |
| GET | `/socios/{id}` | Detalle de un socio |
| PATCH | `/socios/{id}` | Actualizar parcialmente un socio |
| GET | `/reservas` | Listar reservas. Filtros: `id_cancha`, `id_socio`, `estado`, `fecha_desde`, `fecha_hasta` |
| POST | `/reservas` | Crear una reserva |
| GET | `/reservas/{id}` | Detalle de una reserva |
| PUT | `/reservas/{id}/estado` | Cambiar el estado de una reserva |

Los listados admiten `_limit` (entre 1 y 100, por defecto 10) y `_offset`
(mayor o igual a cero, por defecto 0), y devuelven los datos bajo una clave
descriptiva junto a un objeto `_links` con `_first`, `_prev`, `_next` y `_last`.

## Ejemplos de solicitudes

### Deportes

```bash
curl http://localhost:5000/club_reservas_api/deportes
```

```json
{
  "deportes": [
    { "id_deporte": 1, "nombre": "Futbol" },
    { "id_deporte": 2, "nombre": "Tenis" },
    { "id_deporte": 3, "nombre": "Padel" }
  ]
}
```

### Canchas

```bash
# Crear una cancha. El precio va en centavos: 1200000 es $12.000,00
curl -X POST http://localhost:5000/club_reservas_api/canchas \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Futbol 5 - Maracana", "id_deporte": 1, "precio_hora": 1200000, "techada": false}'

# Filtros combinados con paginacion
curl "http://localhost:5000/club_reservas_api/canchas?id_deporte=1&techada=true&activa=true&_limit=5&_offset=0"

# Actualizar el precio. No afecta a las reservas ya registradas
curl -X PATCH http://localhost:5000/club_reservas_api/canchas/1 \
  -H "Content-Type: application/json" \
  -d '{"precio_hora": 1500000}'

# Canchas libres el 15/10 de 18 a 20
curl "http://localhost:5000/club_reservas_api/canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00&hora_fin=20:00"

# Eliminar. Responde 409 si la cancha tiene reservas asociadas
curl -X DELETE http://localhost:5000/club_reservas_api/canchas/1
```

Respuesta de un listado:

```json
{
  "canchas": [
    {
      "id_cancha": 1,
      "nombre": "Futbol 5 - Maracana",
      "id_deporte": 1,
      "precio_hora": 1200000,
      "techada": false,
      "activa": true
    }
  ],
  "_limit": 10,
  "_offset": 0,
  "_links": {
    "_first": "/canchas?_limit=10&_offset=0",
    "_prev": null,
    "_next": null,
    "_last": "/canchas?_limit=10&_offset=0"
  }
}
```

### Socios

```bash
# Registrar. El servidor asigna activo: true
curl -X POST http://localhost:5000/club_reservas_api/socios \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Alejandro Gomez", "email": "alejandro.gomez@email.com"}'

# Busqueda parcial por nombre, sin distinguir mayusculas
curl "http://localhost:5000/club_reservas_api/socios?nombre=gomez&activo=true"

# Baja logica
curl -X PATCH http://localhost:5000/club_reservas_api/socios/1 \
  -H "Content-Type: application/json" \
  -d '{"activo": false}'
```

### Reservas

```bash
# Crear. Las fechas van en ISO 8601 con desplazamiento fijo -03:00
curl -X POST http://localhost:5000/club_reservas_api/reservas \
  -H "Content-Type: application/json" \
  -d '{
    "id_socio": 1,
    "id_cancha": 2,
    "fecha_hora_inicio": "2026-10-15T18:00:00.000000-03:00",
    "fecha_hora_fin": "2026-10-15T20:00:00.000000-03:00"
  }'

# Filtrar por rango de fechas y estado
curl "http://localhost:5000/club_reservas_api/reservas?estado=confirmada&fecha_desde=2026-10-01&fecha_hasta=2026-10-31"

# Cancelar. Solo se permite antes del horario de inicio
curl -X PUT http://localhost:5000/club_reservas_api/reservas/1/estado \
  -H "Content-Type: application/json" \
  -d '{"estado": "cancelada"}'
```

Respuesta de una reserva creada, con la tarifa y el total congelados:

```json
{
  "id_reserva": 1,
  "id_socio": 1,
  "id_cancha": 2,
  "fecha_hora_inicio": "2026-10-15T18:00:00.000000-03:00",
  "fecha_hora_fin": "2026-10-15T20:00:00.000000-03:00",
  "estado": "confirmada",
  "precio_hora_aplicado": 1200000,
  "total": 2400000
}
```

### Formato de error

Todos los errores comparten la misma estructura:

```json
{
  "errors": [
    {
      "code": "reserva.superpuesta.cancha",
      "message": "La cancha ya esta reservada en ese horario",
      "level": "error",
      "description": "La cancha '2' ya tiene una reserva que se superpone con el intervalo solicitado"
    }
  ]
}
```

| Codigo HTTP | Cuando |
|-------------|--------|
| 200 | Consultas y actualizaciones exitosas |
| 201 | Creaciones exitosas |
| 204 | Eliminacion exitosa, sin cuerpo |
| 400 | Parametros o cuerpo invalidos, campos desconocidos, estado desconocido |
| 404 | El recurso referenciado no existe |
| 409 | Correo duplicado, entidad inactiva, superposicion, transicion no permitida, o cancha con reservas |

## Pruebas

La coleccion [`docs/club_reservas_api.postman_collection.json`](docs/club_reservas_api.postman_collection.json)
cubre las pruebas minimas que exige el enunciado. Se importa en Postman y se
ejecuta con el Collection Runner, en orden.

| Carpeta | Cubre |
|---------|-------|
| 0. Preparacion | crea las canchas y socios que usan las demas carpetas |
| 1. Creacion valida, importe y tarifa historica | alta de cancha, socio y reserva; calculo del total; la tarifa no cambia al modificar el precio de la cancha |
| 2. Superposiciones | intervalos identicos, contenidos, contenedores y parciales, para la cancha y para el socio; aceptacion de consecutivas |
| 3. Rechazos de datos invalidos | horarios invalidos, reservas no futuras, referencias inexistentes, entidades inactivas, y verificacion de que no quedaron registros |
| 4. Transiciones de estado | repetir el estado actual, finalizar antes de tiempo, cancelar, reactivar una cancelada, y liberacion del horario |
| 5. Eliminacion y filtros | 409 al borrar una cancha con reservas, 204 sin ellas, filtros combinados con paginacion |

La coleccion calcula las fechas en tiempo de ejecucion, siempre futuras y en
horas en punto, asi que no vence. Solo necesita la API corriendo y los deportes
cargados; no depende de `datos_prueba.sql`.

Si se prefiere la linea de comandos:

```bash
npx newman run docs/club_reservas_api.postman_collection.json \
  --env-var baseUrl=http://localhost:5000/club_reservas_api
```

## Supuestos adoptados

- Todas las fechas y horas se interpretan en GMT-3, sin conversion de zona
  horaria. Se almacenan como `DATETIME` y el desplazamiento `-03:00` se
  reconstruye al serializar la respuesta.
- Los importes se manejan como enteros en centavos: `1000000` es $10.000,00.
- La baja de socios y canchas es logica (`activo` / `activa`). La unica
  eliminacion fisica es la de canchas sin reservas asociadas.
- La unicidad del email de socios aplica tambien contra socios inactivos.
- Los deportes se cargan en `init_db.sql` y no tienen ABM, segun el enunciado.
- Los datos ficticios de socios y canchas se cargan aparte, con
  `db/datos_prueba.sql`, para que levantar la base no dependa de ellos.
- El script de datos de prueba no incluye reservas: al admitirse unicamente
  reservas futuras, cualquier fecha fija quedaria vencida al poco tiempo.

## Como trabajar en este repo

Ver [CONTRIBUTING.md](CONTRIBUTING.md).
