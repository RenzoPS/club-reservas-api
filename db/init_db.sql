-- Esquema y datos iniciales de la base `club`.
--
-- docker-compose monta este archivo en /docker-entrypoint-initdb.d, asi que
-- se ejecuta solo la primera vez que se crea el contenedor.
--
-- Para re-ejecutarlo despues de modificarlo:
--     docker compose down -v && docker compose up -d

-- ====================TABLAS====================
CREATE TABLE club.deportes
	(
	id_deporte INT NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(50) NOT NULL UNIQUE,
	PRIMARY KEY(id_deporte)
	);

CREATE TABLE club.socios
	(
	id_socio INT NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(80) NOT NULL,
	email VARCHAR(255) NOT NULL UNIQUE,
	activo BOOLEAN NOT NULL DEFAULT TRUE,
	PRIMARY KEY(id_socio)
	);

CREATE TABLE club.canchas
	(
	id_cancha INT NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(100) NOT NULL,
	id_deporte INT NOT NULL,
	precio_hora INT NOT NULL, -- centavos: 1000000 = $10.000,00
	techada BOOLEAN NOT NULL DEFAULT FALSE,
	activa BOOLEAN NOT NULL DEFAULT TRUE,
	PRIMARY KEY(id_cancha),

	CONSTRAINT fk_deporte_de_cancha
		FOREIGN KEY (id_deporte)
		REFERENCES club.deportes(id_deporte),

	CONSTRAINT ck_cancha_precio_positivo CHECK (precio_hora > 0)
	);

CREATE TABLE club.reservas
	(
	id_reserva INT NOT NULL AUTO_INCREMENT,
	id_socio INT NOT NULL,
	id_cancha INT NOT NULL,
	-- DATETIME y no TIMESTAMP: TIMESTAMP convierte a UTC segun el time_zone de
	-- la sesion, y el enunciado pide interpretar todo en GMT-3 sin conversion.
	fecha_hora_inicio DATETIME NOT NULL,
	fecha_hora_fin DATETIME NOT NULL,
	estado ENUM('confirmada','cancelada','finalizada') NOT NULL DEFAULT 'confirmada',
	precio_hora_aplicado INT NOT NULL,
	total INT NOT NULL,
	PRIMARY KEY(id_reserva),

	-- Sin ON DELETE: queda RESTRICT, asi borrar una cancha con reservas falla
	-- en la base. El 409 lo devuelve la API, esto es la red de seguridad.
	CONSTRAINT fk_reserva_de_cancha
		FOREIGN KEY (id_cancha)
		REFERENCES club.canchas(id_cancha),

	CONSTRAINT fk_reserva_de_socio
		FOREIGN KEY (id_socio)
		REFERENCES club.socios(id_socio),

	CONSTRAINT ck_reserva_intervalo CHECK (fecha_hora_fin > fecha_hora_inicio),
	CONSTRAINT ck_reserva_precio_positivo CHECK (precio_hora_aplicado > 0),
	CONSTRAINT ck_reserva_total_positivo CHECK (total > 0)
	);