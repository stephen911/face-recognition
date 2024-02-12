# from flask import Flask, render_template, request
# import sqlite3
# from datetime import datetime

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html', selected_date='', no_data=False)

# @app.route('/attendance', methods=['POST'])
# def attendance():
#     selected_date = request.form.get('selected_date')
#     selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
#     formatted_date = selected_date_obj.strftime('%Y-%m-%d')

#     conn = sqlite3.connect('attendance.db')
#     cursor = conn.cursor()

#     cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
#     attendance_data = cursor.fetchall()

#     conn.close()

#     if not attendance_data:
#         return render_template('index.html', selected_date=selected_date, no_data=True)
    
#     return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, Response
import sqlite3
from datetime import datetime
import csv
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT(course) FROM attendance ")
    courses = cursor.fetchall()
    courses = [result[0] for result in courses]
    conn.close()
    return render_template('index.html', selected_date='', courses=courses)

@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    course = request.form.get('course')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, id, time FROM attendance WHERE course = ? AND date = ?", (course, formatted_date,))
    attendance_data = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT(course) FROM attendance ")
    courses = cursor.fetchall()
    courses = [result[0] for result in courses]
    conn.close()


    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, courses=courses, selected_course=course)
    
    return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data, courses=courses, selected_course=course)

@app.route('/export_csv')
def export_csv():
    selected_date = request.args.get('selected_date')
    course = request.args.get('course')
    if not selected_date:
        return "Please select a date."
    if not course:
        return "Please select a course."

    try:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        formatted_date = selected_date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return "Invalid date format."
    # selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    # formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, id, time FROM attendance WHERE course = ? AND date = ?", (course, formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    if not attendance_data:
        return "No attendance data available for the selected date."

    # Create a CSV string in memory
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Name', 'Id', 'Time'])
    csv_writer.writerows(attendance_data)
    
    # Prepare response with CSV data
    csv_data.seek(0)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename=attendance_{formatted_date}.csv'}
    )

# if __name__ == '__main__':
#     app.run(debug=True)