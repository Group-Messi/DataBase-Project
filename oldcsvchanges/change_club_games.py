import pandas as pd

# 1. Dosyanın yolunu belirle
file_path = 'datas/club_games.csv'

# 2. PDF'e göre tutmak istediğimiz 5 sütunun listesi
columns_to_keep = [
    'game_id', 
    'club_id', 
    'hosting', 
    'opponent_goals', 
    'own_goals'
]

try:
    # 3. CSV dosyasını oku
    df = pd.read_csv(file_path)

    # 4. Sadece tutmak istediğimiz sütunları seçerek yeni bir DataFrame oluştur
    df_cleaned = df[columns_to_keep]

    # 5. Temizlenmiş veriyi aynı dosyanın üzerine yaz (index'leri kaydetme)
    df_cleaned.to_csv(file_path, index=False)

    print(f"'{file_path}' başarıyla temizlendi.")
    print(f"Sadece şu sütunlar bırakıldı: {columns_to_keep}")

except FileNotFoundError:
    print(f"HATA: '{file_path}' bulunamadı.")
except KeyError:
    print("HATA: Belirtilen sütunlardan biri veya birkaçı CSV dosyasında bulunamadı.")
    print("Lütfen 'columns_to_keep' listesini kontrol et.")
except Exception as e:
    print(f"Beklenmedik bir hata oluştu: {e}")