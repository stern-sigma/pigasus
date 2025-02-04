DROP DATABASE IF EXISTS test_db;

CREATE DATABASE test_db;

USE test_db;

CREATE TABLE botanist (
    botanist_id INT PRIMARY KEY IDENTITY(1,1),
    email VARCHAR(20),
    name VARCHAR(20) NOT NULL,
    phone_number VARCHAR(20) NOT NULL
);

CREATE TABLE continent (
    continent_id INT PRIMARY KEY IDENTITY(1,1),
    continent_name VARCHAR(10) NOT NULL
);

CREATE TABLE country (
    country_id SMALLINT PRIMARY KEY IDENTITY(1,1),,
    country_code VARCHAR(20) NOT NULL,
    continent_id TINYINT NOT NULL,
)

CREATE TABLE city (
    city_id INT PRIMARY KEY IDENTITY(1,1),
    city_name VARCHAR(20) NOT NULL,
    region_id BIGINT
);

CREATE TABLE region (
    region_id INT PRIMARY KEY IDENTITY(1,1),
    region_name VARCHAR(20),
    country_id SMALLINT
);