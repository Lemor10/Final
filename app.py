from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Dog, Vaccine
import os
from flask import make_response
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import ID_CARD, A7
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('login.html')

# 🐾 USER REGISTRATION
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        contact_number = request.form['contact_number']
        address = request.form['address']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        new_user = User(full_name=full_name, email=email, password=password, contact_number=contact_number, address=address)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 🐾 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# 🐾 DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    dogs = Dog.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', dogs=dogs, user=current_user)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_vaccine/<int:dog_id>', methods=['POST'])
@login_required
def add_vaccine(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    vaccine_name = request.form['vaccine_name']
    date_given = datetime.strptime(request.form['date_given'], '%Y-%m-%d')

    new_vaccine = Vaccination(
        dog_id=dog.id,
        vaccine_name=vaccine_name,
        date_given=date_given
    )
    db.session.add(new_vaccine)

    # Create Reminder Notification (set for 1 year after vaccination)
    reminder_date = date_given + timedelta(days=365)
    reminder_message = f"Reminder: {dog.name} is due for {vaccine_name} vaccination on {reminder_date.strftime('%Y-%m-%d')}."
    reminder = Notification(user_id=current_user.id, message=reminder_message)
    db.session.add(reminder)
    db.session.commit()

    flash("Vaccination added and reminder created!", "success")
    return redirect(url_for('dog_profile', dog_id=dog.id))

# 🐶 ADD DOG
@app.route('/add_dog', methods=['GET', 'POST'])
@login_required
def add_dog():
    if request.method == 'POST':
        name = request.form['name']
        breed = request.form['breed']
        age = request.form['age']
        color = request.form['color']
        gender = request.form['gender']
        photo_file = request.files['photo']

        photo_path = None
        if photo_file and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(photo_path)

        new_dog = Dog(
            name=name,
            breed=breed,
            age=age,
            color=color,
            gender=gender,
            photo=photo_path,
            user_id=current_user.id
        )

        db.session.add(new_dog)
        db.session.commit()

        # Generate QR Code
        qr = qrcode.make(f"http://127.0.0.1:5000/dog/{new_dog.id}")
        qr_path = os.path.join('static/qr_codes', f"dog_{new_dog.id}.png")
        qr.save(qr_path)
        new_dog.qr_code = qr_path
        db.session.commit()

        flash('Dog registered successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_dog.html')

# Custom ID card size (like a small ID)
ID_CARD = (85.6 * mm, 54 * mm)

@app.route('/generate_id/<int:dog_id>')
@login_required
def generate_id(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    if dog.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard'))

    # Create PDF buffer
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=ID_CARD)
    width, height = ID_CARD

    # Add background color or border
    pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.rect(2, 2, width - 4, height - 4, fill=1)

    # Add Dog Photo
    if dog.photo:
        try:
            img_path = os.path.join(app.root_path, dog.photo)
            pdf.drawImage(ImageReader(img_path), 5 * mm, 25 * mm, width=25 * mm, height=25 * mm)
        except:
            pass

    # Dog Info
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(35 * mm, 45 * mm, f"🐾 {dog.name}")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(35 * mm, 40 * mm, f"Breed: {dog.breed}")
    pdf.drawString(35 * mm, 35 * mm, f"Color: {dog.color}")
    pdf.drawString(35 * mm, 30 * mm, f"Gender: {dog.gender}")

    # Owner Info
    owner = User.query.get(dog.user_id)
    pdf.setFont("Helvetica", 7)
    pdf.drawString(5 * mm, 12 * mm, f"Owner: {owner.full_name}")
    pdf.drawString(5 * mm, 8 * mm, f"Contact: {owner.contact_number}")

    # QR Code (existing QR stored in folder)
    qr_path = os.path.join(app.root_path, dog.qr_code)
    try:
        pdf.drawImage(ImageReader(qr_path), width - 25 * mm, 5 * mm, 20 * mm, 20 * mm)
    except:
        pass

    pdf.save()
    buffer.seek(0)

    # Send PDF to browser
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={dog.name}_ID.pdf'
    return response

# 🐕 VIEW DOG PROFILE
@app.route('/dog/<int:dog_id>')
def dog_profile(dog_id):
    dog = Dog.query.get_or_404(dog_id)
    owner = User.query.get(dog.user_id)
    return render_template('dog_profile.html', dog=dog, owner=owner)

@app.route('/mark_read/<int:note_id>')
@login_required
def mark_read(note_id):
    note = Notification.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)
    note.is_read = True
    db.session.commit()
    return redirect(url_for('dashboard'))

# 🐾 LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# AUTO CREATE TABLES
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
