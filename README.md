# Club Reservas API

API REST para gestionar canchas, socios y reservas del Club Deportivo Encuentro.

Trabajo practico de Introduccion al Desarrollo de Software (FIUBA).

## Integrantes

| Nombre | Padron |
|--------|--------|
| | |

## Versiones utilizadas

| Componente | Version |
|------------|---------|
| Python | 3.14.7 |
| Flask | 3.1.3 |
| SQLAlchemy | 2.0.54 |
| mysql-connector-python | 26.7.0 |
| python-dotenv | 1.2.3 |
| flask-swagger-ui | 5.33.0 |
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

_Completar._

## Ejemplos de solicitudes

_Completar._

## Supuestos adoptados

_Completar._

## Como trabajar en este repo

Ver [CONTRIBUTING.md](CONTRIBUTING.md).
