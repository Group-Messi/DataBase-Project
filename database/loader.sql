-- INFILE AYARI
SET GLOBAL local_infile=1;

CREATE DATABASE IF NOT EXISTS football_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE football_db;

-- TEMİZLİK (DROP SIRALAMASI ÖNEMLİ)
DROP TABLE IF EXISTS club_games;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS transfers;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS competitions;
DROP TABLE IF EXISTS countries;

-- 1. COUNTRIES
CREATE TABLE countries (
    country_id INT PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    iso_code VARCHAR(10),
    confederation VARCHAR(20),
    latitude FLOAT,
    longitude FLOAT
) ENGINE=InnoDB;

-- 2. COMPETITIONS
CREATE TABLE competitions (
    competition_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sub_type VARCHAR(100),
    type VARCHAR(100),
    country_id INT,
    url TEXT,
    is_major_national_league BOOLEAN,
    FOREIGN KEY (country_id) REFERENCES countries(country_id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. CLUBS
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
) ENGINE=InnoDB;

-- 4. PLAYERS (DÜZELTİLDİ: SİLİNECEK SÜTUNA FOREIGN KEY VERMEDİK)
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
    current_club_domestic_competition_id VARCHAR(10), -- FK KALDIRILDI (Çünkü silinecek)
    current_club_name VARCHAR(150),
    market_value_in_eur FLOAT,
    highest_market_value_in_eur FLOAT,
    -- current_club_domestic_competition_id İÇİN OLAN FK SATIRINI SİLDİM --
    FOREIGN KEY (current_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- 5. TRANSFERS
CREATE TABLE transfers (
    transfer_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT,
    transfer_date DATE,
    from_club_id INT,
    to_club_id INT,
    transfer_season VARCHAR(10),
    player_name VARCHAR(255),
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (from_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (to_club_id)   REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- 6. CLUB_GAMES
CREATE TABLE club_games (
    game_id BIGINT,
    club_id INT,
    hosting VARCHAR(10),
    opponent_goals INT,
    own_goals INT,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. GAMES
CREATE TABLE games (
    game_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    home_club_id INT,
    away_club_id INT ,
    game_date DATE ,
    home_club_goals SMALLINT DEFAULT 0,
    away_club_goals SMALLINT DEFAULT 0,
    FOREIGN KEY (home_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (away_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================================
-- DATA YÜKLEME
-- ========================================================

LOAD DATA LOCAL INFILE 'datas/countries.csv' INTO TABLE countries FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS (country_id, country_name, iso_code, confederation, latitude, longitude);

-- Competitions için "True" -> 1 dönüşümü
LOAD DATA LOCAL INFILE 'datas/competitions.csv' 
INTO TABLE competitions 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS 
(competition_id, name, sub_type, type, country_id, @dummy_country_name, @dummy_league_code, url, @is_major_text)
SET is_major_national_league = (TRIM(BOTH '\r' FROM @is_major_text) = 'True');

LOAD DATA LOCAL INFILE 'datas/clubs.csv' INTO TABLE clubs FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'datas/players.csv' INTO TABLE players FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'datas/transfers.csv' INTO TABLE transfers FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'datas/club_games.csv' INTO TABLE club_games FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'datas/games.csv' INTO TABLE games FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- ========================================================
-- 3NF DÖNÜŞÜMÜ VE TEMİZLİK (NORMALİZASYON ADIMLARI)
-- ========================================================

-- 1. PLAYERS TABLOSU
-- Artık FK olmadığı için bu satır hata vermeyecek.
ALTER TABLE players
DROP COLUMN current_club_name,
DROP COLUMN current_club_domestic_competition_id,
DROP COLUMN city_of_birth;

-- 2. TRANSFERS TABLOSU
ALTER TABLE transfers
DROP COLUMN player_name;

-- 3. CLUBS TABLOSU
ALTER TABLE clubs
DROP COLUMN total_market_value,
DROP COLUMN squad_size,
DROP COLUMN average_age,
DROP COLUMN foreigners_number,
DROP COLUMN foreigners_percentage,
DROP COLUMN national_team_players,
DROP COLUMN stadium_seats;

-- 4. CLUB_GAMES
ALTER TABLE club_games ADD PRIMARY KEY (game_id, club_id);

-- ÇALIŞTIRMA
-- 1 - CMD AÇIN
-- 2 - projenin root folder'ına geçin (örn: cd "C:\users\alperen\desktop\databaseprojesi")
-- 3 - mysql client çalıştırın ( mysql -u -root -p --local-infile=1 ) (mysql --local-infile=1 -u root -pŞİFRENİBURAYAGİR)
-- 3.not (şifreniz genelde 'root' olur)
-- 4 - bu sql scriptini çalıştırın ( SOURCE database/loader.sql; )