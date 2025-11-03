-- -----------------------------------------------------
-- Database Şeması: transfers2.csv dosyasından türetilmiştir.
-- Dosya Konumu: Projenin Ana Dizini
-- -----------------------------------------------------

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