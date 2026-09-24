-- Tablas

CREATE TABLE club.canchas
	(
	id_cancha INT NOT NULL AUTO_INCREMENT,
	deporte VARCHAR(50) NOT NULL,
	PRIMARY KEY(id_cancha)
	);

CREATE TABLE club.socios
	(
	id_socio INT NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(50) NOT NULL,
	apellido VARCHAR(50) NOT NULL,
	PRIMARY KEY(id_socio)
	);

CREATE TABLE club.reservas
	(
	fecha_inicio TIMESTAMP NOT NULL, -- Solo el inicio es PK para que pinche si se inteta solapar una misma cancha. La fecha fin no es necesaria.
	fecha_fin TIMESTAMP NOT NULL, -- Formato 'YYYY-MM-DD HH:MM:SS'
	id_cancha INT NOT NULL,
	id_socio INT NOT NULL,
	estado VARCHAR(20) NOT NULL, -- confirmada, cancelada, finalizada.
	importe_inicial INT NOT NULL, -- No pongo decimal porque se especifica que sea entero.
	PRIMARY KEY(fecha_inicio, id_cancha)
	);