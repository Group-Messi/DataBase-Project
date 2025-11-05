CREATE TABLE GAMES(
    game_id BIGINT ,
    home_club_id INT NOT NULL,
    away_club_id INT NOT NULL,
    game_date DATE NOT NULL,
    home_club_goals SMALLINT DEFAULT 0,
    away_club_goals SMALLINT DEFAULT 0,

    PRIMARY KEY(game_id)
    FOREIGN KEY(home_club_id)
        REFERENCES CLUBS(club_id) --not created yet
    Foreign KEY(away_club_id)
        REFERENCES CLUBS(club_id) --not created yet also
)