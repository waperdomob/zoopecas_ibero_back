-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Crear usuario administrador por defecto
-- La contraseña se encriptará en el código Python
-- Password: Admin123!

