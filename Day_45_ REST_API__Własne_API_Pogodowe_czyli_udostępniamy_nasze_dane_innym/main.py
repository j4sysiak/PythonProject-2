from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_history.db'
db = SQLAlchemy(app)


# 1. MODEL TABELI (Musimy go mieć, żeby Flask wiedział, jak czytać bazę)
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temp = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(100), nullable=False)

    # METODA POMOCNICZA: Zamienia obiekt z bazy (którego JSON nie rozumie) na zwykły słownik
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# --- 2. ENDPOINT: GET (Zwraca całą historię) ---
@app.route("/api/history", methods=["GET"])
def get_all_history():
    records = db.session.query(SearchHistory).all()
    # Przelatujemy przez wszystkie rekordy, zamieniamy na słowniki i pakujemy w JSON
    return jsonify(history=[record.to_dict() for record in records])


# --- 3. ENDPOINT: GET z filtrowaniem po mieście (Query Parameters) ---
@app.route("/api/search", methods=["GET"])
def search_city():
    # Pobiera z paska adresu parametr ?city=...
    query_city = request.args.get("city")

    # Szukamy w bazie tylko tych wpisów, gdzie miasto się zgadza
    records = db.session.query(SearchHistory).filter_by(city=query_city).all()

    if records:
        # Zwracamy kod 200 (OK) - Flask robi to domyślnie
        return jsonify(results=[record.to_dict() for record in records])
    else:
        # Zwracamy kod 404 (Not Found), jeśli miasta nie było w bazie
        return jsonify(error={"Not Found": "Brak historii dla tego miasta."}), 404




# --- 5. ENDPOINT: POST (Dodawanie nowego rekordu przez API) ---
@app.route("/api/history", methods=["POST"])
def add_record():
    # Odbieramy dane wysłane w "ciele" zapytania (tzw. form-data)
    new_city = request.form.get("city")
    new_temp = request.form.get("temp")

    # Zabezpieczenie: jeśli ktoś wyśle POST, ale zapomni podać miasta lub temperatury
    if not new_city or not new_temp:
        # Kod 400 = Bad Request (Złe żądanie od klienta)
        return jsonify(error={"Bad Request": "Brak parametrów 'city' lub 'temp'."}), 400

    # Tworzymy nowy rekord i pchamy do bazy SQL
    new_record = SearchHistory(
        city=new_city,
        temp=float(new_temp),
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(new_record)
    db.session.commit()

    # Kod 201 = Created (Pomyślnie utworzono nowy zasób na serwerze)
    return jsonify(response={"Success": "Pomyślnie dodano nowy wpis do bazy."}), 201



# --- 4. ENDPOINT: DELETE (Usuwanie z bazy - Wymaga klucza!) ---
@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    # Sprawdzamy, czy programista podał poprawny klucz w adresie ?api_key=...
    api_key = request.args.get("api_key")
    if api_key == "TajneHasloSzefa":
        record_to_delete = db.session.get(SearchHistory, record_id)
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()
            return jsonify(success={"Message": "Rekord usunięty pomyślnie."}), 200
        else:
            return jsonify(error={"Not Found": "Brak rekordu o takim ID."}), 404
    else:
        # Zwracamy kod 403 (Forbidden), gdy klucz jest zły
        return jsonify(error={"Forbidden": "Brak uprawnień. Zły klucz API."}), 403


if __name__ == "__main__":
    app.run(debug=True)