CREATE DATABASE IF NOT EXISTS bd_deportes;

USE bd_deportes;
CREATE TABLE IF NOT EXISTS producto(
id              int             auto_increment  primary key,
nombre          varchar(150)    NOT NULL,
descripcion     varchar(255)    NULL,
stock           int             NOT NULL DEFAULT 0,
precio_unitario decimal(10,2)   NOT NULL DEFAULT 0,
fecha_ingreso   date            NOT NULL,
categoria       varchar(100)    NOT NULL
);