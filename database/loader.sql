-- INFILE'I LOCAL FOLDERA ALIYOR
SET GLOBAL local_infile=1;

CREATE DATABASE IF NOT EXISTS football_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE football_db;

-- DROP TABLE SIRALAMASI ÖNEMLİ (FK BAĞIMLILIKLARI NEDENİYLE)
DROP TABLE IF EXISTS club_games;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS transfers;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS competitions;

-- 1. COMPETITIONS (GÜNCELLENDİ: country_id yerine country_name)
CREATE TABLE competitions (
    competition_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sub_type VARCHAR(100),
    type VARCHAR(100),
    country_name VARCHAR(100), -- Değiştirildi
    url TEXT,
    is_major_national_league BOOLEAN
) ENGINE=InnoDB;

-- 2. CLUBS
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
    FOREIGN KEY (domestic_competition_id)
        REFERENCES competitions(competition_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. PLAYERS
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
    FOREIGN KEY (current_club_domestic_competition_id)
        REFERENCES competitions(competition_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    FOREIGN KEY (current_club_id)
        REFERENCES clubs(club_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 4. TRANSFERS
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

-- 5. CLUB_GAMES
CREATE TABLE club_games (
    game_id BIGINT PRIMARY KEY,
    club_id INT,
    hosting VARCHAR(10),
    opponent_goals INT,
    own_goals INT,
    FOREIGN KEY (club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

-- 6. GAMES
CREATE TABLE games (
    game_id BIGINT PRIMARY KEY,
    home_club_id INT NOT NULL,
    away_club_id INT NOT NULL,
    game_date DATE NOT NULL,
    home_club_goals SMALLINT DEFAULT 0,
    away_club_goals SMALLINT DEFAULT 0,
    FOREIGN KEY (home_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (away_club_id) REFERENCES clubs(club_id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

-- LOAD DATA KISMI
-- CSV yapısı: competition_id, name, sub_type, type, country_id, country_name, domestic_league_code, url, is_major
-- Biz country_id'yi atlayıp (@dummy), country_name'i alacağız.

LOAD DATA LOCAL INFILE 'datas/competitions.csv' 
INTO TABLE competitions 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS
(competition_id, name, sub_type, type, @dummy_country_id, country_name, @dummy_league_code, url, is_major_national_league);

LOAD DATA LOCAL INFILE 'datas/clubs.csv' INTO TABLE clubs FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
LOAD DATA LOCAL INFILE 'datas/players.csv' INTO TABLE players FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
LOAD DATA LOCAL INFILE 'datas/transfers.csv' INTO TABLE transfers FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
LOAD DATA LOCAL INFILE 'datas/club_games.csv' INTO TABLE club_games FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
LOAD DATA LOCAL INFILE 'datas/games.csv' INTO TABLE games FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
-- ÇALIŞTIRMA
-- 1 - CMD AÇIN
-- 2 - projenin root folder'ına geçin (örn: cd "C:\users\alperen\desktop\databaseprojesi")
-- 3 - mysql client çalıştırın ( mysql -u -root -p --local-infile=1 ) (mysql --local-infile=1 -u root -pŞİFRENİBURAYAGİR)
-- 3.not (şifreniz genelde 'root' olur)
-- 4 - bu sql scriptini çalıştırın ( SOURCE database/loader.sql; )

SELECT 
    comp.name AS Competition_Name,      -- Tablo 1: competitions
    c.name AS Club_Name,                -- Tablo 2: clubs
    COUNT(cg.game_id) AS Games_Played,  -- Aggregation
    SUM(cg.own_goals) AS Total_Goals,   -- Aggregation
    AVG(cg.own_goals) AS Avg_Goals
FROM club_games cg                      -- Tablo 3: club_games (Senin tablon)
INNER JOIN clubs c ON cg.club_id = c.club_id
LEFT JOIN competitions comp ON c.domestic_competition_id = comp.competition_id -- OUTER JOIN
INNER JOIN games g ON cg.game_id = g.game_id -- Tablo 4: games (4. tablo şartı)
WHERE cg.hosting = 'Home' 
AND c.total_market_value > (            -- NESTED QUERY (Ortalamadan zengin kulüpler)
    SELECT AVG(total_market_value) 
    FROM clubs 
    WHERE total_market_value IS NOT NULL
)
GROUP BY comp.name, c.name              -- GROUP BY
ORDER BY Total_Goals DESC
LIMIT 10;