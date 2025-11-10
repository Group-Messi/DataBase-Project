from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home_page():
    proje_adi = "Futbol Veritabanı Projesi"
    
    return render_template("main.html", title=proje_adi)

if __name__ == "__main__":
    app.run(debug=True, port=5000)