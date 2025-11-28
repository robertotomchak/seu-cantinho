CREATE DATABASE IF NOT EXISTS seuCantinho;
USE seuCantinho;

CREATE TABLE IF NOT EXISTS client(
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        CPF VARCHAR(11) NOT NULL UNIQUE,
        numeroTel VARCHAR(20),
        nome VARCHAR(255) NOT NULL,
        isAdmin BOOLEAN NOT NULL,
        filial VARCHAR(5),
        wallet INT
);

CREATE TABLE IF NOT EXISTS property(
        id INT AUTO_INCREMENT PRIMARY KEY,
        address VARCHAR(255) NOT NULL UNIQUE,
        contact VARCHAR(20),
        property_name VARCHAR(255) NOT NULL,
        value_per_day INT
);

CREATE TABLE IF NOT EXISTS property_reserves(
        id INT AUTO_INCREMENT PRIMARY KEY,
        renter_id INT NOT NULL, 
        property_id INT NOT NULL,
        initTime TIMESTAMP NOT NULL,
        endTime TIMESTAMP NOT NULL,
        FOREIGN KEY (renter_id) REFERENCES client(id),
        FOREIGN KEY (property_id) REFERENCES property(id)
)

INSERT INTO client (email, password, CPF, numeroTel, nome, isAdmin, filial) 
VALUES ('admin@a', 
        'jhin1234',
        '00000000000',
        NULL,
        'ricardo rei delas',
        1,
        NULL,
        10000)
ON DUPLICATE KEY UPDATE email = email;