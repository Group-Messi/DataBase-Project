
-- transfers2.csv dosyasının verilerini tutacak tablo
CREATE TABLE IF NOT EXISTS transfers (
    -- Birincil Anahtar (Primary Key)
    transfer_id INT PRIMARY KEY, 
    
    -- Oyuncu ve Kulüp ID'leri (Diğer tablolara referans veren sütunlar)
    player_id INT NOT NULL,
    from_club_id INT,
    to_club_id INT,
    
    -- Tarih ve Sezon Bilgileri
    transfer_date DATE, 
    transfer_season VARCHAR(10), 
    
    -- Oyuncu Adı
    player_name VARCHAR(255) NOT NULL,
    
    -- 1. Oyuncu ID'si için Foreign Key
    FOREIGN KEY (player_id) 
        REFERENCES players(player_id)
        ON UPDATE CASCADE             
        ON DELETE RESTRICT,           
    
    -- 2. Geldiği Kulüp ID'si için Foreign Key
    FOREIGN KEY (from_club_id)
        REFERENCES clubs(club_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,           
        
    -- 3. Gittiği Kulüp ID'si için Foreign Key
    FOREIGN KEY (to_club_id)
        REFERENCES clubs(club_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
        
);



-- Bünyamin Kalaycı'nın sorumluluğundaki 'club_games' tablosu (DÜZELTİLMİŞ)

CREATE TABLE club_games (
    -- game_id: 8 haneli (7+1) sayısal ID. BIGINT daha güvenli.
    game_id BIGINT PRIMARY KEY, 
    
    -- club_id: Snippet'ta 1468.0 gibi görünüyor, INT (tamsayı) olmalı.
    club_id INT,
    
    -- hosting: 'Home' veya 'Away' gibi metin. VARCHAR(10) yeterli.
    hosting VARCHAR(10), 
    
    -- Gol sayıları: Snippet'ta 2.0 gibi görünüyor, INT (tamsayı) olmalı.
    opponent_goals INT,
    own_goals INT,
    
    -- 'clubs' tablosuna (extra) olan bağlantı
    FOREIGN KEY (club_id) REFERENCES clubs(club_id)
);

-- Drop tables if they already exist (for re-creation)
DROP TABLE IF EXISTS players;
 
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