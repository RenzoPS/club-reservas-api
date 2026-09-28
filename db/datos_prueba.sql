
-- DATOS DE PRUEBA

-- El cliente de linea de comandos de MySQL asume latin1, asi que interpretaria
-- mal los bytes de los nombres con acento y los guardaria corruptos. SET NAMES
-- le avisa que este archivo viene en utf8mb4.
SET NAMES utf8mb4;

INSERT INTO club.socios (nombre, email, activo) VALUES
('Alejandro Gómez', 'alejandro.gomez@email.com', TRUE),
('María Rodríguez', 'maria.rodriguez@email.com', TRUE),
('Juan Pérez', 'juan.perez@email.com', FALSE),
('Ana Martínez', 'ana.martinez@email.com', TRUE),
('Carlos López', 'carlos.lopez@email.com', TRUE),
('Laura García', 'laura.garcia@email.com', TRUE),
('Diego Fernández', 'diego.fernandez@email.com', FALSE),
('Sofía Sánchez', 'sofia.sanchez@email.com', TRUE),
('Luis Romero', 'luis.romero@email.com', TRUE),
('Elena Díaz', 'elena.diaz@email.com', TRUE);


INSERT INTO club.canchas (nombre, id_deporte, precio_hora, techada, activa) VALUES
('Fútbol 5 - Maracaná', 1, 1500000, FALSE, TRUE),
('Fútbol 5 - Bombonera (Techada)', 1, 1800000, TRUE, TRUE),
('Fútbol 7 - Camp Nou', 1, 2200000, FALSE, TRUE),
('Fútbol 5 - El Potrero (Mantenimiento)', 1, 1200000, FALSE, FALSE),
('Tenis Polvo de Ladrillo 1', 2, 1200000, FALSE, TRUE),
('Tenis Polvo de Ladrillo 2', 2, 1200000, FALSE, TRUE),
('Tenis Cemento - Techada', 2, 1600000, TRUE, TRUE),
('Pádel Cristal 1', 3, 1000000, FALSE, TRUE),
('Pádel Cristal 2 (Techada)', 3, 1400000, TRUE, TRUE),
('Pádel Muro Clásico', 3, 800000, FALSE, TRUE);

