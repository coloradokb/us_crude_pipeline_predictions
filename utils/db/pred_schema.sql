CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY,
    report_date DATE,
    actual_supply INTEGER,
    eia_pred_target_id INTEGER,
    prediction INTEGER,
    updated_date DATE,
    regressor_count INTEGER,
    FOREIGN KEY (eia_pred_target_id) REFERENCES eia_pipelines(id)
);


CREATE TABLE IF NOT EXISTS eia_pipelines (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    description TEXT
);
