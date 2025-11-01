import pandas as pd
from pathlib import Path

# Get directory where this .py file is located
BASE_DIR = Path(__file__).parent

# --- Kayra'nin transfers.csv scripti basliyor ---
print("transfers.csv islemi baslatiliyor...")

# 1. transfers.csv dosyasinin yolunu belirle
transfers_csv_path = BASE_DIR / "transfers.csv"

# 2. CSV'yi oku
df_transfers = pd.read_csv(transfers_csv_path)

# 3. KIRPMA ISLEMI: Sadece gorev tanimindaki sutunlari tut
cols_to_keep = [
    "player_id", 
    "transfer_date", 
    "from_club_id", 
    "to_club_id",
    "transfer_season",  # YENI EKLENDI
    "player_name"       # YENI EKLENDI
]

# Sadece bu sutunlari iceren yeni bir DataFrame olustur
# .copy() ekleyerek "SettingWithCopyWarning" hatasini onluyoruz
df_new = df_transfers[cols_to_keep].copy()

# 4. 'transfer_id'yi olustur (index + 1)
df_new['transfer_id'] = df_new.index + 1

# 5. 'transfer_id' sutununu en basa (loc=0) tasi
# Bilgi kaybi olmadan en basa ekler, digerlerini saga kaydirir
df_new.insert(loc=0, column="transfer_id", value=df_new.pop('transfer_id'))

# 6. Yeni CSV (transfers2.csv) olarak kaydet
output_path = BASE_DIR / 'transfers2.csv'
df_new.to_csv(output_path, index=False)

print(f"transfers2.csv (kirpilmis ve id eklenmis) basariyla olusturuldu: {output_path}")
# --- Kayra'nin scripti bitti ---