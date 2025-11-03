import pandas as pd
from pathlib import Path

# Get directory where this .py file is located
BASE_DIR = Path(__file__).parent

# Build the full path to games.csv
csv_path = BASE_DIR / "games.csv"


df = pd.read_csv(csv_path)

new_df = pd.DataFrame()


cols = ['game_id', 'home_club_id', 'away_club_id', 'date', 'home_club_goals', 'away_club_goals']
new_df = df[cols]



new_df.to_csv('games2.csv', index=False)








