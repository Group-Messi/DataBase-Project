from flask import Flask, render_template_string, request, redirect, url_for
import os  # Ortam değişkenlerini okumak için
from dotenv import load_dotenv  # .env dosyasını yüklemek için
import pymysql
from pymysql.cursors import DictCursor

# --- .ENV YÜKLEME ---
load_dotenv()  # .env dosyasını otomatik olarak yüklüyor
app = Flask(__name__)

# --- VERİTABANI AYARLARI ---
DB_SETTINGS = {
    "host": os.environ.get("MYSQL_HOST"),
    "user": os.environ.get("MYSQL_USER"),
    "password": os.environ.get("MYSQL_PASSWORD"),
    "database": os.environ.get("MYSQL_DATABASE"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "cursorclass": DictCursor,
    "charset": "utf8mb4",
    "autocommit": False,
}


def get_db_connection():
    # Her istek için yeni bağlantı açıp kapatmak MySQL sürücüsüyle güvenli oluyor.
    return pymysql.connect(**DB_SETTINGS)

# --- HTML ŞABLONU (Frontend) ---
# Tek dosyada çalışsın diye HTML'i buraya gömüyoruz.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Group Messi - Yönetim Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        
        /* Başlıklar */
        h1 { text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 15px; }
        h2 { color: #34495e; margin-top: 30px; }

        /* Form Tasarımı */
        .form-box { background: #ecf0f1; padding: 20px; border-radius: 8px; margin-bottom: 30px; }
        .form-row { display: flex; gap: 15px; margin-bottom: 15px; }
        input, select { padding: 10px; border: 1px solid #bdc3c7; border-radius: 4px; flex: 1; }
        button { background-color: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; width: 100%; }
        button:hover { background-color: #2ecc71; }

        /* Tablo Tasarımı */
        .table-container { max-height: 500px; overflow-y: auto; border: 1px solid #bdc3c7; }
        table { width: 100%; border-collapse: collapse; }
        th { background-color: #34495e; color: white; position: sticky; top: 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        tr:hover { background-color: #f1f2f6; }
        
        .badge { padding: 5px 10px; border-radius: 12px; font-size: 0.85em; font-weight: bold; }
        .win { background-color: #d4edda; color: #155724; }
        .loss { background-color: #f8d7da; color: #721c24; }
        .draw { background-color: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚽ Group Messi - Club Games Yönetimi</h1>

        <div class="form-box">
            <h2>➕ Yeni Maç Ekle (Create)</h2>
            <form action="/" method="POST">
                <div class="form-row">
                    <input type="number" name="game_id" placeholder="Game ID (Örn: 999999)" required>
                    <input type="number" name="club_id" placeholder="Club ID (Örn: 1468)" required>
                </div>
                <div class="form-row">
                    <select name="hosting">
                        <option value="Home">Home (Ev Sahibi)</option>
                        <option value="Away">Away (Deplasman)</option>
                    </select>
                    <input type="number" name="own_goals" placeholder="Bizim Goller" required>
                    <input type="number" name="opponent_goals" placeholder="Rakip Goller" required>
                </div>
                <button type="submit">Veritabanına Kaydet</button>
            </form>
        </div>

        <h2>📋 Kayıtlı Maçlar (Read)</h2>
        <p>Son eklenen 100 maç gösteriliyor.</p>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Game ID</th>
                        <th>Kulüp ID/Adı</th>
                        <th>Saha</th>
                        <th>Skor</th>
                    </tr>
                </thead>
                <tbody>
                    {% for game in games %}
                    <tr>
                        <td>{{ game.game_id }}</td>
                        <td>
                            {% if game.club_name %}
                                <b>{{ game.club_name }}</b>
                            {% else %}
                                <span style="color:red">ID: {{ game.club_id }} (Tanımsız)</span>
                            {% endif %}
                        </td>
                        <td>{{ game.hosting }}</td>
                        <td>
                            {% set result = 'draw' %}
                            {% if game.own_goals > game.opponent_goals %}{% set result = 'win' %}{% endif %}
                            {% if game.own_goals < game.opponent_goals %}{% set result = 'loss' %}{% endif %}
                            
                            <span class="badge {{ result }}">
                                {{ game.own_goals }} - {{ game.opponent_goals }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

# --- BACKEND MANTIĞI ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Formdan gelen verileri al ve doğrula
        try:
            game_id = int(request.form['game_id'])
            club_id = int(request.form['club_id'])
            hosting = request.form['hosting']
            own_goals = int(request.form['own_goals'])
            opponent_goals = int(request.form['opponent_goals'])
        except (KeyError, ValueError) as e:
            return f"<h1>Form Hatası:</h1><p>{e}</p>"

        insert_sql = """
            INSERT INTO club_games (game_id, club_id, hosting, own_goals, opponent_goals)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(insert_sql, (game_id, club_id, hosting, own_goals, opponent_goals))
                conn.commit()
            return redirect(url_for('index'))
        except Exception as e:
            return f"<h1>Kayıt Hatası:</h1><p>{e}</p>"

    # GET İsteği: Verileri Listele
    select_sql = """
        SELECT cg.game_id,
               cg.club_id,
               cg.hosting,
               cg.own_goals,
               cg.opponent_goals,
               c.name AS club_name
        FROM club_games cg
        LEFT JOIN clubs c ON cg.club_id = c.club_id
        ORDER BY cg.game_id DESC
        LIMIT 100
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_sql)
                games = cursor.fetchall()
    except Exception as e:
        return f"<h1>Veri Çekme Hatası:</h1><p>{e}</p>"

    return render_template_string(HTML_TEMPLATE, games=games)

if __name__ == '__main__':
    # Eğer .env'de port tanımlıysa onu kullan, yoksa 5001 kullan
    port = int(os.environ.get('PORT', 5001)) 
    app.run(debug=True, port=port)