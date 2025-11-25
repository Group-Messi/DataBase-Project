import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 1. .env Dosyasını Yüklüyoruz
load_dotenv() 

# 2. Bağlantıyı Kuruyoruz
db_connection_str = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}".format(
    user=os.environ.get('MYSQL_USER'),
    password=os.environ.get('MYSQL_PASSWORD'),
    host=os.environ.get('MYSQL_HOST'),
    port=os.environ.get('MYSQL_PORT'),
    db=os.environ.get('MYSQL_DATABASE')
)
db_connection = create_engine(db_connection_str)

try:
    print("⏳ Ligler (Competitions) okunuyor...")
    # csv dosyasının ismi sende farklı olabilir, datas klasörüne bak (örn: competitions.csv)
    df = pd.read_csv('datas/competitions.csv', encoding='utf-8')
    
    print(f"📄 {len(df)} lig bulundu. Veritabanına yazılıyor...")

    # Veritabanına Yüklüyoruz
    df.to_sql('competitions', con=db_connection, if_exists='append', index=False)
    
    print("✅ BAŞARILI: Ligler yüklendi!")

except Exception as e:
    print("❌ HATA:")
    print(e)