from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
import sqlite3
import pandas as pd

app = Flask(__name__)

# Set up upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to render the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission and file upload
@app.route('/submit', methods=['POST'])
def submit():
    if 'frontImage' not in request.files or 'backImage' not in request.files or 'profileImage' not in request.files:
        return 'No file part', 400
    
    name = request.form.get('name')
    phone = request.form.get('phone')
    
    front_image = request.files['frontImage']
    back_image = request.files['backImage']
    profile_image = request.files['profileImage']
    
    if not (front_image and back_image and profile_image):
        return 'No image selected for upload', 400
    
    # Secure filenames and save the files
    front_filename = secure_filename(front_image.filename)
    back_filename = secure_filename(back_image.filename)
    profile_filename = secure_filename(profile_image.filename)
    
    front_filepath = os.path.join(app.config['UPLOAD_FOLDER'], front_filename)
    back_filepath = os.path.join(app.config['UPLOAD_FOLDER'], back_filename)
    profile_filepath = os.path.join(app.config['UPLOAD_FOLDER'], profile_filename)
    
    front_image.save(front_filepath)
    back_image.save(back_filepath)
    profile_image.save(profile_filepath)
    
    # Store file paths in the database
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            front_image TEXT,
            back_image TEXT,
            profile_image TEXT
        )
    ''')
    c.execute('''
        INSERT INTO users (name, phone, front_image, back_image, profile_image)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, phone, front_filepath, back_filepath, profile_filepath))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# Route to export data to an Excel sheet
@app.route('/export')
def export_to_excel():
    conn = sqlite3.connect('users.db')
    query = "SELECT * FROM users"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Save to Excel
    df.to_excel('users_data.xlsx', index=False, engine='openpyxl')
    return "Data exported to Excel"

if __name__ == '__main__':
    app.run(debug=True)
