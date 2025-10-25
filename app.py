from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os

from config import Config
from models import db, User, Dog, Vaccine

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create database tables (on first run)
with app.app_context():
    db.create_all()

# ---------------------------
# Helper Functions
# ---------------------------
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ---------------------------
# Routes
# ---------------------------

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# ---------------------------
# User Registration
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        contact = request.form['contact']
        address = request.form['address']

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            return redirect(url_for('register'))

        new_user = User(
            full_name=full_name, email=email, password=password,
            contact_number=contact, address=address
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# ---------------------------
# User Login
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Welcome back!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "danger")

    return render_template('login.html')

# ---------------------------
# User Logout
# ---------------------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# ---------------------------
# Dashboard
# ---------------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    dogs = Dog.query.filter_by(user_id=user.id).all()

    # Simple vaccine reminders
    today = date.today()
    reminders = Vaccine.query.filter(Vaccine.next_due_date != None, Vaccine.next_due_date <= today).all()

    return render_template('dashboard.html', user=user, dogs=dogs, reminders=reminders)

# ---------------------------
# Add Dog
# ---------------------------
@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        breed = request.form['breed']
        color = request.form['color']
        gender = request.form['gender']
        age = request.form['age']

        photo = request.files['photo']
        filename = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_dog = Dog(
            user_id=session['user_id'], name=name, breed=breed, color=color,
            gender=gender, age=age, photo_url=filename
        )

        db.session.add(new_dog)
        db.session.commit()
        flash("Dog profile added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_dog.html')

# ---------------------------
# Add Vaccine
# ---------------------------
@app.route('/add_vaccine/<int:dog_id>', methods=['GET', 'POST'])
def add_vaccine(dog_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    dog = Dog.query.get_or_404(dog_id)

    if request.method == 'POST':
        vaccine_name = request.form['vaccine_name']
        date_given = datetime.strptime(request.form['date_given'], '%Y-%m-%d').date()
        next_due_date = request.form.get('next_due_date')
        vet_name = request.form['vet_name']

        cert = request.files['certificate']
        cert_filename = None
        if cert and allowed_file(cert.filename):
            cert_filename = secure_filename(cert.filename)
            cert.save(os.path.join(app.config['UPLOAD_FOLDER'], cert_filename))

        new_vaccine = Vaccine(
            dog_id=dog.id,
            vaccine_name=vaccine_name,
            date_given=date_given,
            next_due_date=datetime.strptime(next_due_date, '%Y-%m-%d').date() if next_due_date else None,
            vet_name=vet_name,
            certificate_url=cert_filename
        )

        db.session.add(new_vaccine)
        db.session.commit()
        flash("Vaccine record added!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_vaccine.html', dog=dog)

# ---------------------------
# Run App
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
