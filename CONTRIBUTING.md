# Como trabajar en este repo

Guia para el equipo. Si nunca usaste git, segui los pasos tal cual estan.

## Reglas

1. **Nunca se pushea a `main` ni a `dev` directo.** Siempre rama + Pull Request.
2. `main` queda para la entrega final. Trabajamos sobre `dev`.
3. Antes de empezar a trabajar, SIEMPRE traer los ultimos cambios.
4. PR chico y temprano: apenas tengas **un** endpoint andando, abrilo. No esperes a terminar todo.
5. Si algo no te cierra, preguntá en el grupo antes de inventar.

## Setup inicial (una sola vez)

Los pasos completos, con las variantes de Windows y que hacer si algo falla,
estan en el [README](README.md#instalacion).

Resumen para Linux / macOS:

```bash
git clone <url-del-repo>
cd club-reservas-api

cp .env.example .env
docker compose up -d

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python app.py
```

Hace falta Python 3.10 o superior. Verificar con `python3 --version`.

**Si cambia `db/init_db.sql`**, el contenedor no vuelve a ejecutarlo solo: el
volumen ya tiene datos. Para aplicar el esquema nuevo hay que destruirlo:

```bash
docker compose down -v && docker compose up -d
```

Esto borra los datos de tu base local y los recarga desde el script. Pasa cada
vez que alguien mergea un cambio de esquema, asi que conviene tenerlo a mano.

## El ciclo de trabajo

### 1. Traer lo ultimo

```bash
git checkout dev
git pull origin dev
```

Esto **siempre**, antes de crear tu rama. Si trabajas sobre codigo viejo, despues el merge duele.

### 2. Crear tu rama

```bash
git checkout -b feat/canchas
```

Formato del nombre: `feat/<lo-que-hacés>`, en minusculas y con guiones.

### 3. Trabajar y guardar

```bash
git status                        # ver que cambio
git add .                         # sumar todo lo cambiado
git commit -m "feat(canchas): agregar GET /canchas con filtros"
```

Formato del mensaje: `tipo(alcance): que hiciste`

- `feat(socios): validar unicidad de email`
- `fix(reservas): corregir calculo del total`
- `docs(readme): agregar ejemplos de requests`

Commiteá seguido. Un commit por cosa que funciona, no uno gigante al final.

### 4. Subir la rama

```bash
git push -u origin feat/canchas
```

La primera vez lleva `-u origin <rama>`. Despues alcanza con `git push`.

### 5. Abrir el Pull Request

1. Entrá al repo en GitHub
2. Te va a aparecer el cartel **"Compare & pull request"**. Clic ahi
3. **Importante**: verificá que diga `base: dev` ← `compare: feat/tu-rama`. Si dice `base: main`, cambialo
4. **Create pull request**
5. Avisá en el grupo

No mergees tu propio PR.

### 6. Si te piden cambios

Seguis en la misma rama, commiteás y pusheás de nuevo. El PR se actualiza solo.

```bash
git add .
git commit -m "fix(canchas): rechazar precio_hora negativo"
git push
```

### 7. Cuando se mergea

```bash
git checkout dev
git pull origin dev
```

Y arrancás la proxima rama desde ahi.

## Si aparece un conflicto

GitHub te va a decir *"This branch has conflicts that must be resolved"*.

**No toques nada y avisá en el grupo.** Un conflicto mal resuelto borra trabajo de otro.

Para evitarlos:

- `git pull origin dev` seguido, no una vez por semana
- Trabajá solo en tus archivos
- Si dos personas comparten un archivo, coordinen y pulleen antes de cada sesion

## Que NO se commitea

Ya esta en `.gitignore`, pero por las dudas:

- `.env` — configuracion local, cada uno tiene el suyo
- `venv/` — son miles de archivos, se regenera con `pip install -r requirements.txt`
- `__pycache__/` — temporales de Python

Si ves alguno de esos en `git status`, algo esta mal. Avisá antes de commitear.

## Donde va cada cosa

```
app.py                      arranque, registra los blueprints
club_reservas/
  constants.py              configuracion
  repositories/             el SQL
  routes/                   los endpoints HTTP
  services/                 la logica de negocio
  validators/               validacion del input
db/init_db.sql              esquema y datos
docs/swagger.yaml           el contrato de la API
```

Un archivo por recurso en cada capa. El flujo de una request es:

```
routes/  ->  services/  ->  repositories/
 (HTTP)      (negocio)         (SQL)
```
