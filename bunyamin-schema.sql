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