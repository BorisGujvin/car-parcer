CREATE TABLE IF NOT EXISTS advertisements(
    id int PRIMARY KEY UNIQUE,
    brand VARCHAR(50),
    model VARCHAR(100) NOT NULL,
    name VARCHAR(200),
    photo_link VARCHAR(200),
    year int,
    volume VARCHAR(50),
    mileage VARCHAR(50),
    price VARCHAR(50)
);
