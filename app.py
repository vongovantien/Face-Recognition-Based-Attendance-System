import base64
from datetime import datetime

import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
dbname = "tvmjqhoc"
user = "tvmjqhoc"
password = "RgOxjyMaN0PMiaDlzU1ZWG6S14N3Lypi"
host = "rain.db.elephantsql.com"

# Updated PostgreSQL connection details
DATABASE_URL = f"dbname='{dbname}' user='{user}' host='{host}' password='{password}'"

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, time, date, image FROM attendance ORDER BY date DESC, time DESC LIMIT 10")
    attendance_data = cursor.fetchall()
    for i, row in enumerate(attendance_data):
        name, time, date, image = row
        image_base64 = base64.b64encode(image).decode('utf-8') if image else None
        attendance_data[i] = (name, time, date, image_base64)

    conn.close()
    return render_template('index.html', attendance_data=attendance_data, no_data=False)


@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    person_type = request.form.get('person_type')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = get_db_connection()
    cursor = conn.cursor()
    if person_type == 'unknown':
        cursor.execute("""
            SELECT name, time, date, image 
            FROM attendance 
            WHERE date = %s AND name = 'Unknown person'
        """, (formatted_date,))
    elif person_type is None and selected_date is None:
        cursor.execute("""
            SELECT name, time, date, image 
            FROM attendance 
            ORDER BY date DESC, time DESC 
            LIMIT 10
        """)
    else:
        cursor.execute("""
            SELECT name, time, date, image 
            FROM attendance 
            WHERE date = %s AND name != 'Unknown person'
        """, (formatted_date,))
    attendance_data = cursor.fetchall()

    for i, row in enumerate(attendance_data):
        name, time, date, image = row
        image_base64 = base64.b64encode(image).decode('utf-8') if image else None
        attendance_data[i] = (name, time, date, image_base64)

    conn.close()

    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, no_data=True)

    return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data)


if __name__ == '__main__':
    app.run(debug=True)
