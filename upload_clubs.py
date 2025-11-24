import pandas as pd
from sqlalchemy import create_engine

# 1. MySQL Bağlantısını Kuruyoruz
# FORMAT: mysql+pymysql://KULLANICI:SIFRE@HOST/VERITABANI
# Buraya kendi şifreni yaz!
db_connection_str = 'mysql+pymysql://root:adanaMERKEZ@localhost/football_db'
db_connection = create_engine(db_connection_str)

try:
    # 2. CSV dosyasını Pandas ile okuyoruz
    # encoding='utf-8' diyerek Türkçe karakter sorununu baştan çözüyoruz
    # Bazen dosya 'latin1' olabilir, hata alırsan burayı değiştiririz ama genelde utf-8'dir.
    df = pd.read_csv('datas/clubs.csv', encoding='utf-8')
    
    # 3. Veriyi temizleyelim (Veritabanındaki tabloyla uyuşmayan sütun varsa diye)
    # Tablonda olmayan sütunlar varsa Pandas hata verebilir, o yüzden sadece gerekli olanları seçebilirsin.
    # Şimdilik direkt atmayı deneyelim, Pandas akıllıdır.
    
    # 4. Veritabanına Yüklüyoruz
    # if_exists='append': Tablo zaten var, verileri içine ekle demek.
    # index=False: Pandas'ın kendi index numaralarını veritabanına yazma demek.
    df.to_sql('clubs', con=db_connection, if_exists='append', index=False)
    
    print("✅ BAŞARILI: 'clubs' tablosu veritabanına yüklendi!")
    print(f"Toplam {len(df)} satır eklendi.")

except Exception as e:
    print("❌ BİR HATA OLUŞTU:")
    print(e)