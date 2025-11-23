# Bu fonksiyon club_games tablosuna yeni veri eklemek için taslak (CRUD - Create)
def create_club_game(game_id, club_id, hosting, opponent_goals, own_goals):
    """
    Veritabanına yeni bir club_game satırı ekler.
    Parametreler:
    - game_id: Maçın ID'si (integer)
    - club_id: Takımın ID'si
    - hosting: 'Home' veya 'Away'
    - opponent_goals: Rakip gol sayısı
    - own_goals: Kendi gol sayısı
    """
    
    # SQL Sorgusu (Taslak)
    sql_query = """
    INSERT INTO club_games (game_id, club_id, hosting, opponent_goals, own_goals)
    VALUES (%s, %s, %s, %s, %s);
    """
    
    # Veri demeti
    data = (game_id, club_id, hosting, opponent_goals, own_goals)
    
    print(f"Eklenecek SQL: {sql_query}")
    print(f"Veriler: {data}")
    
    return True

if __name__ == "__main__":
    # Test çalışması
    create_club_game(23204501, 1468, 'Home', 2, 0)