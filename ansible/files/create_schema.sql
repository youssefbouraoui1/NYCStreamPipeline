CREATE TABLE IF NOT EXISTS traffic_incidents (
    id SERIAL PRIMARY KEY,
    incident_timestamp TIMESTAMP NOT NULL,
    borough VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    street_name VARCHAR(100),
    injured_persons INTEGER,
    killed_persons INTEGER,
    vehicle_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id TIMESTAMP PRIMARY KEY,
    crash_date DATE,
    day_of_week TEXT,
    month TEXT,
    hour_of_day INT,
    year INT
);

CREATE TABLE IF NOT EXISTS dim_location (
    location_id UUID PRIMARY KEY, 
    borough TEXT,
    zip_code TEXT,
    on_street_name TEXT,
    cross_street_name TEXT,
    off_street_name TEXT
);

CREATE TABLE IF NOT EXISTS dim_vehicle (
    vehicle_id UUID PRIMARY KEY,
    vehicle_type TEXT,
    vehicle_position INT 
);

CREATE TABLE IF NOT EXISTS dim_contributing_factor (
    factor_id UUID PRIMARY KEY,  
    factor_description TEXT,
    factor_position INT  
);

CREATE TABLE IF NOT EXISTS fact_incidents (
    incident_id UUID PRIMARY KEY,
    date_id DATE REFERENCES dim_date(date_id),
    location_id UUID REFERENCES dim_location(location_id),
    vehicle_id UUID REFERENCES dim_vehicle(vehicle_id),  
    contributing_factor_id UUID REFERENCES dim_contributing_factor(factor_id),  
    number_of_persons_injured INT,
    number_of_persons_killed INT,
    number_of_motorist_injured INT,
    number_of_motorist_killed INT,
    number_of_pedestrians_injured INT,
    number_of_pedestrians_killed INT,
    number_of_cyclist_injured INT,
    number_of_cyclist_killed INT,
    number_of_incidents INT DEFAULT 1
);

CREATE INDEX idx_fact_date ON fact_incidents(date_id);
CREATE INDEX idx_fact_location ON fact_incidents(location_id);
CREATE INDEX idx_fact_vehicle ON fact_incidents(vehicle_id);
CREATE INDEX idx_fact_factor ON fact_incidents(contributing_factor_id);

CREATE TABLE mv_incidents_by_borough_month (borough TEXT, month TEXT, year INT, total_injured BIGINT, total_killed BIGINT);

CREATE TABLE mv_top_streets_by_injuries (on_street_name TEXT, total_injured BIGINT);

CREATE TABLE mv_vehicle_type_incidents (vehicle_type TEXT, vehicle_position INT, total_incidents BIGINT, total_killed BIGINT);

CREATE TABLE mv_incidents_by_borough_hour (borough TEXT, hour_of_day INT, year INT, month TEXT, day_of_week TEXT, total_incidents BIGINT, total_injured BIGINT, total_killed BIGINT);




--for null values INSERT INTO dim_contributing_factor (factor_description, factor_position) VALUES ('UNKNOWN', 1);

