USE cryptodb;

CREATE TABLE IF NOT EXISTS ucry_index (
    type VARCHAR,
    start_date DATE,
    end_date DATE,
    doc_count INT CHECK (doc_count >= 0),
    index_value DECIMAL,
);
