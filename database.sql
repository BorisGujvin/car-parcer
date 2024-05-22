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
    link VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    active_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE UNIQUE INDEX IF NOT EXISTS advertisements_unique ON advertisements(id, provider);


CREATE TABLE IF NOT EXISTS leads(
	id BIGINT(20) NOT NULL AUTO_INCREMENT,
    provider_name VARCHAR(50) NOT NULL,
    provider_id VARCHAR(50) NOT NULL,
    provider_lead_url VARCHAR(200),
    brand VARCHAR(50),
    car_name VARCHAR(200),
    country VARCHAR(3),
    vat_rate int,
    price_with_vat DOUBLE,
    price_without_vat DOUBLE,
    vat DOUBLE,
    currency VARCHAR(3),
    mileage_km int,
    images JSON,
    created_at TIMESTAMP,    
    active_at TIMESTAMP,
    year int,
    engine VARCHAR(50),
    is_dealer smallint,
    city VARCHAR(50),
    PRIMARY KEY (`id`) USING BTREE
);
