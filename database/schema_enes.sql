-- ========================================
-- Database Schema for Transfermarkt Dataset
-- ========================================

-- Drop tables if they already exist (Order matters due to foreign keys)
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS competitions;

-- ======================
-- Table: competitions
-- ======================
CREATE TABLE competitions (
    competition_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sub_type VARCHAR(100),
    type VARCHAR(100),
    country_id INT,
    country_name VARCHAR(100),
    domestic_league_code VARCHAR(20),
    url TEXT,
    is_major_national_league BOOLEAN
);

-- ======================
-- Table: clubs
-- ======================
CREATE TABLE clubs (
    club_id INT PRIMARY KEY,
    club_code VARCHAR(100),
    name VARCHAR(150),
    domestic_competition_id VARCHAR(10),
    total_market_value FLOAT, -- Data temizlenince float olacak
    squad_size INT,
    average_age FLOAT,
    foreigners_number INT,
    foreigners_percentage FLOAT,
    national_team_players INT,
    stadium_name VARCHAR(150),
    stadium_seats INT,
    net_transfer_record VARCHAR(50), -- "+€3.05m" formatında geldiği için String tutuyoruz
    coach_name VARCHAR(100),
    last_season INT,
    filename TEXT,
    url TEXT,
    
    -- Foreign keys
    FOREIGN KEY (domestic_competition_id) 
        REFERENCES competitions(competition_id) 
        ON UPDATE CASCADE 
        ON DELETE SET NULL
);

-- ======================
-- Table: players
-- ======================
CREATE TABLE players ( 
    player_id INT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    name VARCHAR(150),
    last_season INT,
    current_club_id INT,
    player_code VARCHAR(100),
    country_of_birth VARCHAR(100),
    city_of_birth VARCHAR(100),
    country_of_citizenship VARCHAR(100),
    date_of_birth DATE,
    sub_position VARCHAR(100),
    position VARCHAR(100),
    foot VARCHAR(10),
    height_in_cm FLOAT,
    contract_expiration_date VARCHAR(50),
    image_url TEXT,
    url TEXT,
    current_club_domestic_competition_id VARCHAR(10),
    current_club_name VARCHAR(150),
    market_value_in_eur FLOAT,
    highest_market_value_in_eur FLOAT,

    -- Foreign keys
    FOREIGN KEY (current_club_domestic_competition_id)
        REFERENCES competitions(competition_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (current_club_id)
        REFERENCES clubs(club_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);