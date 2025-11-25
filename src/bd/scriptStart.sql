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
        filial VARCHAR(5)
);

INSERT INTO client (email, password, CPF, numeroTel, nome, isAdmin, filial) 
VALUES ('admin@a', 
        'jhin1234',
        '00000000000',
        NULL,
        'ricardo rei delas',
        1,
        NULL)
ON DUPLICATE KEY UPDATE email = email;