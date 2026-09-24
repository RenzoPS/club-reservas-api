-- Esquema y datos iniciales de la base `club`.
--
-- docker-compose monta este archivo en /docker-entrypoint-initdb.d, asi que
-- se ejecuta solo la primera vez que se crea el contenedor.
--
-- Para re-ejecutarlo despues de modificarlo:
--     docker compose down -v && docker compose up -d

CREATE TABLE club.socios
	(
	id_socio INT NOT NULL AUTO_INCREMENT,
	nombre_completo VARCHAR(80) NOT NULL,
	mail VARCHAR(30) NOT NULL,
	estado_activo VARCHAR(1) NOT NULL, -- booleano S/N
	PRIMARY KEY(id_socio)
	);

CREATE TABLE club.deportes
	(
	id_deporte INT NOT NULL AUTO_INCREMENT,
	nombre_deporte VARCHAR(20) NOT NULL,
	PRIMARY KEY(id_deporte)
	);
	
CREATE TABLE club.canchas
	(
	id_cancha INT NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(20) NOT NULL,
	techada VARCHAR(1) NOT NULL, -- booleano S/N
	estado_activa VARCHAR(1) NOT NULL, -- booleano S/N
	precio_hora INT NOT NULL,
	id_deporte INT NOT NULL,
	PRIMARY KEY(id_cancha),
	
  CONSTRAINT fk_deporte_de_cancha
	FOREIGN KEY (id_deporte) 
	REFERENCES club.deportes(id_deporte)
	ON DELETE SET NULL
	);

CREATE TABLE club.reservas
	(
	fecha_hora_inicio TIMESTAMP NOT NULL,
	fecha_hora_fin TIMESTAMP NOT NULL,
	id_cancha INT NOT NULL,
	id_socio INT NOT NULL,
	estado VARCHAR(20) NOT NULL, -- confirmada, cancelada, finalizada.
	importe_inicial INT NOT NULL, -- No pongo decimal porque se especifica que sea entero.
	PRIMARY KEY(fecha_hora_inicio, id_cancha, estado),
	
  CONSTRAINT fk_reserva_de_cancha
	FOREIGN KEY (id_cancha) 
	REFERENCES club.canchas(id_cancha)
	ON DELETE SET NULL,
	
  CONSTRAINT fk_reserva_de_socio
	FOREIGN KEY (id_socio)
	REFERENCES club.socios(id_socio)
	ON DELETE SET NULL
	);
