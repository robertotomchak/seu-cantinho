CREATE DATABASE IF NOT EXISTS seuCantinho;
USE seuCantinho;

CREATE TABLE IF NOT EXISTS client(
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        CPF VARCHAR(11) NOT NULL UNIQUE,
        numeroTel VARCHAR(20),
        nome VARCHAR(255) NOT NULL,
        isAdmin BOOLEAN NOT NULL DEFAULT(FALSE),
        filial VARCHAR(5),
        wallet INT DEFAULT(0)
);

CREATE TABLE IF NOT EXISTS property(
        id INT AUTO_INCREMENT PRIMARY KEY,
        address VARCHAR(255) NOT NULL UNIQUE,
        contact VARCHAR(20),
        property_name VARCHAR(255) NOT NULL,
        value_per_day INT,
        capacity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS property_reserves(
        id INT AUTO_INCREMENT PRIMARY KEY,
        renter_id INT NOT NULL, 
        property_id INT NOT NULL,
        initTime TIMESTAMP NOT NULL,
        endTime TIMESTAMP NOT NULL,
        FOREIGN KEY (renter_id) REFERENCES client(id) ON DELETE CASCADE,
        FOREIGN KEY (property_id) REFERENCES property(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments(
        id INT AUTO_INCREMENT PRIMARY KEY,
        value INT NOT NULL,
        renter_id INT NOT NULL,
        reserve_id INT,
        FOREIGN KEY (renter_id) REFERENCES client(id) ON DELETE CASCADE,
        FOREIGN KEY (reserve_id) REFERENCES property_reserves(id)
        ON DELETE SET NULL
);

INSERT INTO client (email, password, CPF, numeroTel, nome, isAdmin, filial, wallet) 
VALUES ('user@admin', 
        'strongpassword',
        '00000000000',
        NULL,
        'Admin',
        1,
        NULL,
        10000)
ON DUPLICATE KEY UPDATE email = email;