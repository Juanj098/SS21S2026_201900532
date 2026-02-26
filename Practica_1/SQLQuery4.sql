USE Practica1_semi2;
GO

/* ===============================
   DROP TABLES (orden correcto)
================================ */

IF OBJECT_ID('equipaje', 'U') IS NOT NULL DROP TABLE equipaje;
IF OBJECT_ID('pagos', 'U') IS NOT NULL DROP TABLE pagos;
IF OBJECT_ID('reservas', 'U') IS NOT NULL DROP TABLE reservas;
IF OBJECT_ID('vuelos', 'U') IS NOT NULL DROP TABLE vuelos;
IF OBJECT_ID('pasajeros', 'U') IS NOT NULL DROP TABLE pasajeros;
IF OBJECT_ID('aeropuertos', 'U') IS NOT NULL DROP TABLE aeropuertos;
IF OBJECT_ID('aerolineas', 'U') IS NOT NULL DROP TABLE aerolineas;
GO

/* ===============================
   TABLA: aerolineas
================================ */
CREATE TABLE aerolineas (
    id_aerolinea INT IDENTITY(1,1) PRIMARY KEY,
    codigo_aerolinea VARCHAR(10) NOT NULL,
    nombre_aerolinea VARCHAR(100) NOT NULL
);
GO

/* ===============================
   TABLA: aeropuertos
================================ */
CREATE TABLE aeropuertos (
    id_aeropuerto INT IDENTITY(1,1) PRIMARY KEY,
    codigo_aeropuerto VARCHAR(10) NOT NULL
);
GO

/* ===============================
   TABLA: pasajeros
================================ */
CREATE TABLE pasajeros (
    id_pasajero INT IDENTITY(1,1) PRIMARY KEY,
    genero VARCHAR(10),
    edad INT,
    nacionalidad VARCHAR(50)
);
GO

/* ===============================
   TABLA: vuelos
================================ */
CREATE TABLE vuelos (
    id_vuelo INT IDENTITY(1,1) PRIMARY KEY,
    id_registro INT,
    id_aerolinea INT NOT NULL,
    numero_vuelo VARCHAR(20),
    id_aeropuerto_origen INT NOT NULL,
    id_aeropuerto_destino INT NOT NULL,
    fecha_hora_salida DATETIME2,
    fecha_hora_llegada DATETIME2,
    duracion_minutos INT,
    estado_vuelo VARCHAR(50),
    tipo_aeronave VARCHAR(50),

    CONSTRAINT FK_vuelos_aerolineas
        FOREIGN KEY (id_aerolinea)
        REFERENCES aerolineas(id_aerolinea),

    CONSTRAINT FK_vuelos_aeropuerto_origen
        FOREIGN KEY (id_aeropuerto_origen)
        REFERENCES aeropuertos(id_aeropuerto),

    CONSTRAINT FK_vuelos_aeropuerto_destino
        FOREIGN KEY (id_aeropuerto_destino)
        REFERENCES aeropuertos(id_aeropuerto)
);
GO

/* ===============================
   TABLA: reservas
================================ */
CREATE TABLE reservas (
    id_reserva INT IDENTITY(1,1) PRIMARY KEY,
    id_pasajero INT NOT NULL,  -- Cambiado de VARCHAR(50) a INT
    id_vuelo INT NOT NULL,
    fecha_hora_reserva DATETIME2,
    clase_cabina VARCHAR(20),
    asiento VARCHAR(10),
    canal_venta VARCHAR(50),

    CONSTRAINT FK_reservas_pasajeros
        FOREIGN KEY (id_pasajero)
        REFERENCES pasajeros(id_pasajero),

    CONSTRAINT FK_reservas_vuelos
        FOREIGN KEY (id_vuelo)
        REFERENCES vuelos(id_vuelo)
);
GO

/* ===============================
   TABLA: pagos
================================ */
CREATE TABLE pagos (
    id_pago INT IDENTITY(1,1) PRIMARY KEY,
    id_reserva INT NOT NULL UNIQUE,
    metodo_pago VARCHAR(50),
    precio_boleto DECIMAL(10,2),
    moneda VARCHAR(10),
    precio_estimado_usd DECIMAL(10,2),

    CONSTRAINT FK_pagos_reservas
        FOREIGN KEY (id_reserva)
        REFERENCES reservas(id_reserva)
);
GO

/* ===============================
   TABLA: equipaje
================================ */
CREATE TABLE equipaje (
    id_equipaje INT IDENTITY(1,1) PRIMARY KEY,
    id_reserva INT NOT NULL UNIQUE,
    total_maletas INT,
    maletas_documentadas INT,

    CONSTRAINT FK_equipaje_reservas
        FOREIGN KEY (id_reserva)
        REFERENCES reservas(id_reserva)
);
GO

ALTER TABLE aerolineas
ADD CONSTRAINT UQ_codigo_aerolinea UNIQUE (codigo_aerolinea);

SELECT * FROM pasajeros;

SELECT * FROM aerolineas;

SELECT * FROM aeropuertos;

SELECT * FROM vuelos;

DELETE FROM aerolineas;
DELETE FROM pasajeros;

SELECT COUNT(*) FROM aerolineas;
SELECT COUNT(*) FROM vuelos;

DELETE FROM equipaje;
DELETE FROM pagos;
DELETE FROM reservas;
DELETE FROM vuelos;
DELETE FROM pasajeros;
DELETE FROM aeropuertos;
DELETE FROM aerolineas;

SELECT COUNT(*) FROM pasajeros;

