CREATE DATABASE football_db;
USE football_db;  -- <--- İŞTE BU SATIR ÇOK ÖNEMLİ!

-- Önce temizlik yapıyoruz
DROP TABLE IF EXISTS club_games;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS transfers;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS competitions;

-- Şimdi tabloları oluşturuyoruz
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

CREATE TABLE clubs (
    club_id INT PRIMARY KEY,
    club_code VARCHAR(100),
    name VARCHAR(150),
    domestic_competition_id VARCHAR(10),
    total_market_value FLOAT,
    squad_size INT,
    average_age FLOAT,
    foreigners_number INT,
    foreigners_percentage FLOAT,
    national_team_players INT,
    stadium_name VARCHAR(150),
    stadium_seats INT,
    net_transfer_record VARCHAR(50),
    coach_name VARCHAR(100),
    last_season INT,
    filename TEXT,
    url TEXT,
    FOREIGN KEY (domestic_competition_id) REFERENCES competitions(competition_id) ON UPDATE CASCADE ON DELETE SET NULL
);

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
    FOREIGN KEY (current_club_domestic_competition_id) REFERENCES competitions(competition_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (current_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS transfers (
    transfer_id INT AUTO_INCREMENT PRIMARY KEY, 
    player_id INT NOT NULL,
    from_club_id INT,
    to_club_id INT,
    transfer_date DATE, 
    transfer_season VARCHAR(10), 
    player_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON UPDATE CASCADE ON DELETE RESTRICT,            
    FOREIGN KEY (from_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE SET NULL,            
    FOREIGN KEY (to_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE club_games (
    game_id BIGINT PRIMARY KEY, 
    club_id INT,
    hosting VARCHAR(10), 
    opponent_goals INT,
    own_goals INT,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id)
);

CREATE TABLE games (
    game_id BIGINT,
    home_club_id INT NOT NULL,
    away_club_id INT NOT NULL,
    game_date DATE NOT NULL,
    home_club_goals SMALLINT DEFAULT 0,
    away_club_goals SMALLINT DEFAULT 0,
    PRIMARY KEY(game_id),
    FOREIGN KEY(home_club_id) REFERENCES clubs(club_id),
    FOREIGN KEY(away_club_id) REFERENCES clubs(club_id)
);