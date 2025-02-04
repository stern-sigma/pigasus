DROP DATABASE IF EXISTS plant_db;

CREATE DATABASE plant_db;

USE plant_db;

CREATE TABLE botanist (
    botanist_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    email VARCHAR(20),
    name VARCHAR(20) NOT NULL,
    phone_number VARCHAR(20) NOT NULL
);

CREATE TABLE continent (
    continent_id TINYINT PRIMARY KEY IDENTITY(1,1),
    continent_name VARCHAR(10) NOT NULL
);

CREATE TABLE country (
    country_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    country_code VARCHAR(20) NOT NULL,
    continent_id TINYINT NOT NULL,
    FOREIGN KEY (continent_id) REFERENCES continent(continent_id)
);

CREATE TABLE region (
    region_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    region_name VARCHAR(20),
    country_id SMALLINT,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE city (
    city_id INT PRIMARY KEY IDENTITY(1,1),
    city_name VARCHAR(20) NOT NULL,
    region_id SMALLINT,
    FOREIGN KEY (region_id) REFERENCES region(region_id)
);

CREATE TABLE location (
    location_id INT PRIMARY KEY IDENTITY(1,1),
    latitude DECIMAL NOT NULL,
    longitude DECIMAL NOT NULL,
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE license (
    license_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    license_name TEXT NOT NULL,
    license_url TEXT NOT NULL
);

CREATE TABLE image (
    image_id INT PRIMARY KEY IDENTITY(1,1),
    license_id SMALLINT,
    original_url TEXT NOT NULL,
    medium_url TEXT,
    small_url TEXT,
    regular_url TEXT,
    thumbnail_url TEXT
    FOREIGN KEY (license_id) REFERENCES license(license_id)
);

CREATE TABLE plant (
    plant_id INT PRIMARY KEY IDENTITY(1,1),
    location_id INT NOT NULL,
    scientific_name VARCHAR(30),
    image_id INT,
    common_name VARCHAR(30) NOT NULL,
    FOREIGN KEY (image_id) REFERENCES image(image_id),
    FOREIGN KEY (location_id) REFERENCES location(location_id)
);

CREATE TABLE reading (
    reading_id INT PRIMARY KEY IDENTITY(1,1),
    plant_id INT NOT NULL,
    soil_moisture DECIMAL NOT NULL,
    temperature DECIMAL NOT NULL,
    at DATETIME NOT NULL,
    botanist_id SMALLINT NOT NULL,
    last_watered DATETIME,
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);


