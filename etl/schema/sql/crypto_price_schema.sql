USE cryptodb;

CREATE TABLE IF NOT EXISTS crypto_price (
    currency VARCHAR,
    date DATE,
    open DECIMAL,
    close DECIMAL,
    high DECIMAL,
    low DECIMAL
);
