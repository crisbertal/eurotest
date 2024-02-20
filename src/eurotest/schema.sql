DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS pais;

CREATE TABLE usuario (
  id INTEGER PRIMARY KEY,
  nombre TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  -- check if boolean
  is_admin INTEGER
);

CREATE TABLE pais (
  id INTEGER PRIMARY KEY,
  nombre TEXT UNIQUE NOT NULL,
  -- mean for values between 0 - 10
  interpretacion REAL, 
  vestuario REAL, 
  escenografia REAL, 
  originalidad REAL, 
  espiritu_eurovisivo REAL, 
  -- check if values in [0, 1, 2]
  cae_bien INTEGER
);

