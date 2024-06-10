GRANT ALL PRIVILEGES ON *.* TO 'maxscale_user'@'%';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS dogs;
USE dogs;

DROP TABLE IF EXISTS dogs;  -- Ensures the table doesn't exist already

CREATE TABLE dogs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    breed VARCHAR(255) NOT NULL
);

INSERT INTO dogs (name, breed) VALUES ('Rex', 'German Shepherd');
INSERT INTO dogs (name, breed) VALUES ('Max', 'Beagle');
INSERT INTO dogs (name, breed) VALUES ('Bella', 'Golden Retriever');
