USE plants;

DROP TABLE IF EXISTS alpha.reading;
DROP TABLE IF EXISTS alpha.plant; 
DROP TABLE IF EXISTS alpha.image;
DROP TABLE IF EXISTS alpha.location;
DROP TABLE IF EXISTS alpha.city;
DROP TABLE IF EXISTS alpha.region;
DROP TABLE IF EXISTS alpha.country;
DROP TABLE IF EXISTS alpha.botanist;
DROP TABLE IF EXISTS alpha.continent;
DROP TABLE IF EXISTS alpha.license;

CREATE TABLE alpha.botanist (
    botanist_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    email VARCHAR(20),
    name VARCHAR(20) NOT NULL,
    phone_number VARCHAR(20) NOT NULL
);

CREATE TABLE alpha.continent (
    continent_id TINYINT PRIMARY KEY IDENTITY(1,1),
    continent_name VARCHAR(10) NOT NULL
);

CREATE TABLE alpha.country (
    country_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    country_code VARCHAR(20) NOT NULL,
    continent_id TINYINT NOT NULL,
    FOREIGN KEY (continent_id) REFERENCES alpha.continent(continent_id)
);

CREATE TABLE alpha.region (
    region_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    region_name VARCHAR(20),
    country_id SMALLINT,
    FOREIGN KEY (country_id) REFERENCES alpha.country(country_id)
);

CREATE TABLE alpha.city (
    city_id INT PRIMARY KEY IDENTITY(1,1),
    city_name VARCHAR(20) NOT NULL,
    region_id SMALLINT,
    FOREIGN KEY (region_id) REFERENCES alpha.region(region_id)
);

CREATE TABLE alpha.location (
    location_id INT PRIMARY KEY IDENTITY(1,1),
    latitude DECIMAL NOT NULL,
    longitude DECIMAL NOT NULL,
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES alpha.city(city_id)
);

CREATE TABLE alpha.license (
    license_id SMALLINT PRIMARY KEY IDENTITY(1,1),
    license_name TEXT NOT NULL,
    license_url TEXT NOT NULL
);

CREATE TABLE alpha.image (
    image_id INT PRIMARY KEY IDENTITY(1,1),
    license_id SMALLINT,
    original_url TEXT NOT NULL,
    medium_url TEXT,
    small_url TEXT,
    regular_url TEXT,
    thumbnail_url TEXT,
    FOREIGN KEY (license_id) REFERENCES alpha.license(license_id)
);

CREATE TABLE alpha.plant (
    plant_id INT PRIMARY KEY IDENTITY(1,1),
    location_id INT NOT NULL,
    scientific_name VARCHAR(30),
    image_id INT,
    common_name VARCHAR(30) NOT NULL,
    FOREIGN KEY (image_id) REFERENCES alpha.image(image_id),
    FOREIGN KEY (location_id) REFERENCES alpha.location(location_id)
);

CREATE TABLE alpha.reading (
    reading_id INT PRIMARY KEY IDENTITY(1,1),
    plant_id INT NOT NULL,
    soil_moisture DECIMAL NOT NULL,
    temperature DECIMAL NOT NULL,
    at DATETIME NOT NULL,
    botanist_id SMALLINT NOT NULL,
    last_watered DATETIME NOT NULL,
    FOREIGN KEY (botanist_id) REFERENCES alpha.botanist(botanist_id),
    FOREIGN KEY (plant_id) REFERENCES alpha.plant(plant_id)
);


