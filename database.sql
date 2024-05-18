CREATE TABLE IF NOT EXISTS advertisements(
    id int NOT NULL,
    provider VARCHAR(50) NOT NULL,
    brand VARCHAR(50),
    model VARCHAR(100),
    name VARCHAR(200),
    photo_link VARCHAR(200),
    year int,
    volume VARCHAR(50),
    mileage int,
    price VARCHAR(50),
    is_dealer smallint,
    city VARCHAR(50),
    link VARCHAR(100)
);

CREATE UNIQUE INDEX IF NOT EXISTS advertisements_unique ON advertisements(id, provider);
