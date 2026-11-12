
-- =========================================
-- DATABASE: STORE API
-- =========================================

CREATE DATABASE IF NOT EXISTS db_store;

USE db_store;

-- =========================================
-- TABLE: users
-- Stores login and authentication information
-- =========================================

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('USER', 'MERCHANT') NOT NULL DEFAULT 'USER'
);


-- =========================================
-- TABLE: merchants
-- Stores merchant profile information
-- =========================================

CREATE TABLE merchants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL UNIQUE,
    store_name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL

    FOREIGN KEY (id_user)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================
-- TABLE: products
-- Stores products belonging to merchants
-- =========================================

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_merchant INT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    description  VARCHAR(255) NOT NULL,
    price INT NOT NULL,
    stock INT NOT NULL DEFAULT 0,

    FOREIGN KEY (id_merchant)
        REFERENCES merchants(id)
        ON DELETE CASCADE
);


-- =========================================
-- TABLE: claims
-- Stores customer product claims
-- =========================================

CREATE TABLE claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    id_product INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_user)
        REFERENCES users(id),

    FOREIGN KEY (id_product)
        REFERENCES products(id)
);
