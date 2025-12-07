import pandas as pd
from sqlalchemy import create_engine
import os                       # Ortam değişkenlerini okumak için
from dotenv import load_dotenv  # .env dosyasını yüklemek için

# 1. .env Dosyasını Yüklüyoruz
load_dotenv() 

# 2. MySQL Bağlantısını Kuruyoruz (.env'den okuyarak)
# Bağlantı dizesini dinamik oluşturuyoruz
db_connection_str = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
    user=os.environ.get('MYSQL_USER'),
    password=os.environ.get('MYSQL_PASSWORD'),
    host=os.environ.get('MYSQL_HOST'),
    port=os.environ.get('MYSQL_PORT'),
    db=os.environ.get('MYSQL_DATABASE')
)

db_connection = create_engine(db_connection_str)

try:
    print("⏳ Dosya okunuyor...")
    # 3. CSV dosyasını Pandas ile okuyoruz
    # 'datas/clubs.csv' dosyasının projenin ana dizinindeki 'datas' klasöründe olduğundan emin ol!
    df = pd.read_csv('datas/clubs.csv', encoding='utf-8')
    
    # İsteğe Bağlı: Sütun isimlerini veritabanıyla eşleşecek şekilde temizleyebilirsin
    # Örn: df.columns = [c.lower() for c in df.columns] 
    
    print(f"📄 {len(df)} satır veri okundu. Veritabanına yazılıyor...")

    # 4. Veritabanına Yüklüyoruz
    # if_exists='append': Var olan tablonun altına ekle
    # index=False: Pandas indexlerini yazma
    df.to_sql('clubs', con=db_connection, if_exists='append', index=False)
    
    print("✅ BAŞARILI: 'clubs.csv' verileri 'clubs' tablosuna yüklendi!")

except Exception as e:
    print("❌ BİR HATA OLUŞTU:")
    print(e)
    print("\n💡 İPUCU: Eğer 'Foreign key constraint fails' hatası alıyorsan,")
    print("önce 'competitions' (ligler) tablosunu yüklemen gerekebilir.")