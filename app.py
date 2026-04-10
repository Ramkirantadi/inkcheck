import os
import cv2
import numpy as np
import uuid
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import model_from_json

# --- NEW: Authentication & Database Libraries ---
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialize the Flask web application
app = Flask(__name__)
app.secret_key = "super_cool_secret_key" 
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure the secure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- 1. INITIALIZE DATABASE & SECURITY ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Define the User Database Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 2. LOAD THE DEEP LEARNING MODEL ---
MODEL_DIR = 'model'
json_path = os.path.join(MODEL_DIR, 'model100.json')
weights_path = os.path.join(MODEL_DIR, 'model100.weights.h5')

with open(json_path, 'r') as json_file:
    loaded_model_json = json_file.read()

model = model_from_json(loaded_model_json)
model.load_weights(weights_path)
print("System Initialized: Colab CNN Model loaded successfully!")

# --- 3. OPENCV PREPROCESSING PIPELINE ---
def preprocess_signature(image_path):
    """
    Processes the uploaded signature to perfectly match how the Colab model was trained.
    """
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(img_rgb, (64, 64))
    normalized = resized / 255.0
    return np.expand_dims(normalized, axis=0)

# --- 4. SECURE AUTHENTICATION ROUTING ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))
            
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return redirect(url_for('register'))
            
        # Hash password and save to DB
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        # Check password hash
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    # NO flash() call here — page just silently redirects to login
    return redirect(url_for('login'))

@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/about')
def about():
    return render_template('about.html')

# --- 5. SIGNATURE VERIFICATION ROUTING ---
@app.route('/')
@login_required
def index():
    # Only authenticated users can see the upload portal
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_signature():
    if 'file' not in request.files:
        return redirect(request.url)
        
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
        
    if file:
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Run Preprocessing & Inference
        processed_img = preprocess_signature(filepath)
        prediction = model.predict(processed_img)
        score = float(prediction[0][0])
        
        if score > 0.5:
            result = "Genuine"
            confidence = round(score * 100, 2)
        else:
            result = "Forgery"
            confidence = round((1 - score) * 100, 2)
            
        return render_template('result.html', result=result, confidence=confidence, image_url=filename)

if __name__ == '__main__':
    # Initialize the database file if it doesn't exist yet
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)



# 2. Add these two new routes for Team and About pages

@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/about')
def about():
    return render_template('about.html')