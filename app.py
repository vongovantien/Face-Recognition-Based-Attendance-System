import sqlite3
from datetime import datetime

from flask import Flask, render_template, request

app = Flask(__name__)

import base64


@app.route('/')
def index():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, time, date, image FROM attendance ORDER BY date DESC, time DESC LIMIT 10")
    attendance_data = cursor.fetchall()
    for i, row in enumerate(attendance_data):
        id, name, description, image = row
        image_base64 = base64.b64encode(image).decode('utf-8') if image else None
        # Replace the tuple in the list with a new tuple including the encoded image
        attendance_data[i] = (id, name, description, image_base64)

    conn.close()
    return render_template('index.html', attendance_data=attendance_data, no_data=False)


@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    person_type = request.form.get('person_type')
    print(selected_date)
    print(person_type)
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    if person_type == 'unknown':
        # Fetch records for 'Unknown person' on the specified date
        cursor.execute("""
            SELECT name, time, date, image 
            FROM attendance 
            WHERE date = ? AND name = 'Unknown person'
        """, (formatted_date,))
    elif person_type is None and selected_date is None:
        # Fetch the latest 10 records if no person_type or date is specified
        cursor.execute("""
            SELECT name, time, date, image 
            FROM attendance 
            ORDER BY date DESC, time DESC 
            LIMIT 10
        """)
    else:
        # Fetch records for known persons on the specified date
        cursor.execute("""
            SELECT name, time, date, image 
            FROM attendance 
            WHERE date = ? AND name != 'Unknown person'
        """, (formatted_date,))
    attendance_data = cursor.fetchall()

    print(attendance_data)
    for i, row in enumerate(attendance_data):
        id, name, description, image = row
        image_base64 = base64.b64encode(image).decode('utf-8') if image else None
        # Replace the tuple in the list with a new tuple including the encoded image
        attendance_data[i] = (id, name, description, image_base64)

    conn.close()

    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, no_data=True)

    return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data)


if __name__ == '__main__':
    app.run(debug=True)
