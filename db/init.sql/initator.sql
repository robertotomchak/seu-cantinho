-- Cria o banco de dados se ele não existir (já deve existir devido ao MYSQL_DATABASE=app_db)
-- CREATE DATABASE IF NOT EXISTS app_db;
-- USE app_db;

-- Tabela Espaços (Microsserviço de Espaços)
CREATE TABLE IF NOT EXISTS spaces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    capacity INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

-- Tabela Reservas (Microsserviço de Reservas)
CREATE TABLE IF NOT EXISTS reserves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    space_id INT NOTATORS,
    user_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'CANCELED') DEFAULT 'PENDING',
    FOREIGN KEY (space_id) REFERENCES spaces(id)
);

-- Insere um dado de teste
INSERT INTO spaces (name, capacity) VALUES ('Sala de Reunião 1', 10);