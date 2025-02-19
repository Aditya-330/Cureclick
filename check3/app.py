from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os

# ....................Comments have been added in the code...................#

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cureclick.db'
app.config['SECRET_KEY'] = 'your-secret-key-here'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Admin(UserMixin,db.Model):
    "Admin model"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=True)


class User(UserMixin, db.Model):
    """User model for patients"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Doctor(UserMixin, db.Model):
    """Doctor model with professional details"""
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer)
    city = db.Column(db.String(50))
    fees = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))
    password_hash = db.Column(db.String(128))
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Appointment(db.Model):
    """Appointment model containing all booking details"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    illness = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Confirmed')
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

def set_password(self, password):
    """Create hashed password for new user"""
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    """Check hashed password for login"""
    return check_password_hash(self.password_hash, password)

# User loader callback for Flask-Login
# @login_manager.user_loader
# def load_user(user_id):
#     """Load user based on the route - either doctor or patient"""
#     if 'doctor' in request.path:
#         return Doctor.query.get(int(user_id))
#     return User.query.get(int(user_id))

# @login_manager.user_loader
# def load_user(user_id):
#     # First try User model

#     user = User.query.get(int(user_id))
#     if user:
#         return user
#     # Then try Doctor model
#     return Doctor.query.get(int(user_id))


@login_manager.user_loader
def load_user(user_id):
    # Try Admin first
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    # Then try User
    user = User.query.get(int(user_id))
    if user:
        return user
    # Finally try Doctor
    return Doctor.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('You need to be logged in as an admin to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Routes for User Authentication
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """Handle user login"""
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#         # Find user by username
#         user = User.query.filter_by(username=username).first()
        
#         # Verify password and log in if correct
#         if user and check_password_hash(user.password_hash, password):
#             login_user(user)
#             return redirect(url_for('index'))
#         flash('Invalid username or password', 'error')
#     return render_template('login.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user and admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Try admin login first
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
            
        # Then try regular user login
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
            
        flash('Invalid username or password', 'error')
    return render_template('login.html')


# # Add these routes after the existing appointment routes

# @app.route('/update-appointment/<int:appointment_id>', methods=['GET', 'POST'])
# @login_required
# def update_appointment(appointment_id):
#     """Handle appointment updates"""
#     # Get the appointment
#     appointment = Appointment.query.get_or_404(appointment_id)
    
#     # Verify the appointment belongs to current user
#     if appointment.patient_id != current_user.id:
#         flash('You do not have permission to edit this appointment', 'error')
#         return redirect(url_for('my_appointments'))
    
#     if request.method == 'GET':
#         # Pre-populate the session with existing appointment data
#         session['appointment_data'] = {
#             'first_name': appointment.first_name,
#             'last_name': appointment.last_name,
#             'contact': appointment.contact,
#             'gender': appointment.gender,
#             'age': appointment.age,
#             'city': Doctor.query.get(appointment.doctor_id).city,
#             'illness': appointment.illness,
#             'appointment_id': appointment_id  # Store appointment ID for update
#         }
#         return render_template('appointment_form.html', 
#                              appointment=appointment,
#                              edit_mode=True)
    
#     elif request.method == 'POST':
#         # Update session with new form data
#         session['appointment_data'] = {
#             'first_name': request.form.get('first_name'),
#             'last_name': request.form.get('last_name'),
#             'contact': request.form.get('contact'),
#             'gender': request.form.get('gender'),
#             'age': int(request.form.get('age')),
#             'city': request.form.get('city'),
#             'illness': request.form.get('illness'),
#             'appointment_id': appointment_id
#         }
#         return redirect(url_for('select_doctor'))

# @app.route('/confirm-appointment-update', methods=['POST'])
# @login_required
# def confirm_appointment_update():
#     """Handle the final update of an appointment"""
#     if 'appointment_data' not in session:
#         return redirect(url_for('my_appointments'))
    
#     data = session['appointment_data']
#     appointment_id = data.get('appointment_id')
    
#     if not appointment_id:
#         flash('Invalid appointment update request', 'error')
#         return redirect(url_for('my_appointments'))
    
#     # Get the existing appointment
#     appointment = Appointment.query.get_or_404(appointment_id)
    
#     # Verify ownership
#     if appointment.patient_id != current_user.id:
#         flash('You do not have permission to edit this appointment', 'error')
#         return redirect(url_for('my_appointments'))
    
#     # Update appointment details
#     appointment.doctor_id = data['doctor_id']
#     appointment.appointment_date = datetime.strptime(data['time_slot'].split(' ')[0], '%Y-%m-%d').date()
#     appointment.time_slot = data['time_slot'].split(' ', 1)[1]
#     appointment.illness = data['illness']
#     appointment.first_name = data['first_name']
#     appointment.last_name = data['last_name']
#     appointment.contact = data['contact']
#     appointment.age = data['age']
#     appointment.gender = data['gender']
    
#     try:
#         db.session.commit()
#         flash('Appointment updated successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash('Error updating appointment. Please try again.', 'error')
#         app.logger.error(f'Error updating appointment: {str(e)}')
    
#     # Clear session data
#     session.pop('appointment_data', None)
    
#     return redirect(url_for('my_appointments'))

# # Update the appointment_summary route to handle both new and edit modes
# @app.route('/appointment-summary', methods=['GET', 'POST'])
# @login_required
# def appointment_summary():
#     """Show appointment summary before confirmation"""
#     if request.method == 'POST':
#         doctor_id = request.form.get('doctor_id')
#         time_slot = request.form.get('time_slot')
        
#         # Get doctor details
#         doctor = Doctor.query.get(doctor_id)
        
#         # Update session with doctor and time slot
#         appointment_data = session.get('appointment_data', {})
#         appointment_data['doctor_id'] = doctor.id
#         appointment_data['time_slot'] = time_slot
#         appointment_data['date'] = time_slot.split(' ')[0]
#         session['appointment_data'] = appointment_data
        
#         # Check if this is an edit or new appointment
#         is_edit = 'appointment_id' in appointment_data
        
#         return render_template('appointment_summary.html', 
#                              appointment=appointment_data,
#                              doctor=doctor,
#                              is_edit=is_edit)
#     return redirect(url_for('book_appointment'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))

        # Create new user with hashed password
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    session.pop('username', None)
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard showing doctors list and options"""
    doctors = Doctor.query.all()
    return render_template('admin_dashboard.html', doctors=doctors)

# Routes for Doctor Authentication
@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Handle doctor login"""
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        password = request.form.get('password')
        # Find doctor by doctor_id
        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
        
        # Verify password and log in if correct
        if doctor and check_password_hash(doctor.password_hash, password):
            login_user(doctor)
            return redirect(url_for('doctor_dashboard'))
        flash('Invalid doctor ID or password', 'error')
    return render_template('doctor_login.html')

@app.route('/doctor/logout')
@login_required
def doctor_logout():
    """Handle doctor logout"""
    logout_user()
    return redirect(url_for('doctor_login'))

# Home Page
@app.route('/')
def index():
    """Render homepage"""
    app.logger.debug(f'current_user: {current_user.is_authenticated}')
    if "username" in session:
        return render_template('index.html', username=session['username'])
    return render_template('index.html')

# Appointment Routes
@app.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    """Initial appointment booking form"""
    if request.method == 'POST':
        # Store form data in session for next step
        session['appointment_data'] = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'contact': request.form.get('contact'),
            'gender': request.form.get('gender'),
            'age': int(request.form.get('age')),
            'city': request.form.get('city'),
            'illness': request.form.get('illness')
        }
        return redirect(url_for('select_doctor'))
    return render_template('appointment_form.html')

@app.route('/clear-session')
def clear_session():
    session.clear()
    return redirect(url_for('home'))

# @app.route('/doctors')
# def doctors():
#     return render_template('doctors.html')


@app.route('/select-doctor', methods=['GET', 'POST'])
@login_required
# def select_doctor():
#     """Doctor selection based on city and illness"""
#     if 'appointment_data' not in session:
#         return redirect(url_for('book_appointment'))
    
#     # Get city and illness from session
#     # city = session['appointment_data']['city']
#     # illness = session['appointment_data']['illness']
    
#     # # Filter doctors by city and specialization
#     # doctors = Doctor.query.filter_by(city=city, specialization=illness).all()
def select_doctor():
    """Doctor selection based on city and illness"""
    if 'appointment_data' not in session:
        return redirect(url_for('book_appointment'))
    
    # Get city and illness from session and convert to lowercase
    city = session['appointment_data']['city'].strip().lower()
    illness = session['appointment_data']['illness'].strip().lower()
    
    # Filter doctors by city and specialization (case insensitive)
    doctors = Doctor.query.filter(
        db.func.lower(Doctor.city) == city,
        db.func.lower(Doctor.specialization) == illness
    ).all()
    
    # return render_template('select_doctor.html', doctors=doctors)

    # Generate available slots for each doctor (in real app, this would come from a calendar system)
    for doctor in doctors:
        doctor.available_slots = [
            f"{(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')} {slot}"
            for i in range(1, 8)
            for slot in ['09:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM', '4:00 PM']
        ]
    
    return render_template('doctor_selection.html', doctors=doctors)

@app.route('/appointment-summary', methods=['GET', 'POST'])
@login_required
def appointment_summary():
    """Show appointment summary before confirmation"""
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        time_slot = request.form.get('time_slot')
        
        # Get doctor details
        doctor = Doctor.query.get(doctor_id)
        
        # Update session with doctor and time slot
        appointment_data = session.get('appointment_data', {})
        appointment_data['doctor_id'] = doctor.id
        appointment_data['time_slot'] = time_slot
        appointment_data['date'] = time_slot.split(' ')[0]
        session['appointment_data'] = appointment_data
        
        return render_template('appointment_summary.html', 
                             appointment=appointment_data,
                             doctor=doctor)
    return redirect(url_for('book_appointment'))

# @app.route('/edit-appointment')
# @login_required
# def edit_appointment():
#     """Return to appointment form to edit details"""
#     return redirect(url_for('book_appointment'))

@app.route('/confirm-appointment', methods=['POST'])
@login_required
def confirm_appointment():
    """Finalize and save appointment to database"""
    if 'appointment_data' not in session:
        return redirect(url_for('book_appointment'))
    
    data = session['appointment_data']
    
    # Create new appointment
    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=data['doctor_id'],
        appointment_date=datetime.strptime(data['time_slot'].split(' ')[0], '%Y-%m-%d').date(),
        time_slot=data['time_slot'].split(' ', 1)[1],
        illness=data['illness'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        contact=data['contact'],
        age=data['age'],
        gender=data['gender']
    )
    
    # Save to database
    db.session.add(appointment)
    db.session.commit()
    
    # Clear session data
    session.pop('appointment_data', None)
    
    flash('Appointment confirmed successfully!', 'success')
    return redirect(url_for('my_appointments'))

@app.route('/my-appointments')
@login_required
def my_appointments():
    """Show user's appointments"""
    # Get all appointments for current user
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    # appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    
    # Get doctor details for each appointment
    for appointment in appointments:
        doctor = Doctor.query.get(appointment.doctor_id)
        appointment.doctor_name = doctor.name if doctor else "Unknown"
        
    return render_template('my_appointments.html', appointments=appointments)

@app.route('/cancel-appointment', methods=['POST'])
@login_required
def cancel_appointment():
    """Cancel an existing appointment"""
    appointment_id = request.form.get('appointment_id')
    appointment = Appointment.query.get(appointment_id)
    
    # Verify appointment belongs to current user
    if appointment and appointment.patient_id == current_user.id:
        appointment.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled successfully', 'success')
    else:
        flash('Invalid appointment or permission denied', 'error')
        
    return redirect(url_for('my_appointments'))

# Doctor Dashboard
@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    """Show doctor's dashboard with appointments and earnings"""
    # Get today's date
    today = datetime.now().date()
    
    # Get today's confirmed appointments
    today_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        appointment_date=today,
        status='Confirmed'
    ).all()
    
    # Get future confirmed appointments
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == current_user.id,
        Appointment.appointment_date > today,
        Appointment.status == 'Confirmed'
    ).order_by(Appointment.appointment_date).all()
    
    # Calculate monthly earnings
    first_day_of_month = datetime(today.year, today.month, 1).date()
    last_day_of_month = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).date() if today.month < 12 else datetime(today.year + 1, 1, 1).date() - timedelta(days=1)
    
    monthly_appointments = Appointment.query.filter(
        Appointment.doctor_id == current_user.id,
        Appointment.appointment_date >= first_day_of_month,
        Appointment.appointment_date <= last_day_of_month,
        Appointment.status == 'Confirmed'
    ).count()
    
    monthly_earnings = current_user.fees * monthly_appointments
    
    return render_template('doctor_dashboard.html',
                          doctor=current_user,
                          today_appointments=today_appointments,
                          upcoming_appointments=upcoming_appointments,
                          monthly_earnings=monthly_earnings)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.route('/profile')
@login_required
def profile():
    
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    
    return render_template('profile.html', 
                         appointments=appointments,
                         current_user=current_user)

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

@app.route('/about')
def about():
    """Render about page"""
    return render_template('about.html')

@app.route('/whyus')
def why():
    """Render why us page"""
    return render_template('whyus.html')

@app.route('/admin/add-doctor', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    """Add new doctor to the system"""
    if request.method == 'POST':
        # Generate unique doctor_id
        last_doctor = Doctor.query.order_by(Doctor.id.desc()).first()
        new_doctor_id = f"DOC{(last_doctor.id + 1) if last_doctor else 1}"
        
        doctor = Doctor(
            doctor_id=new_doctor_id,
            name=request.form.get('name'),
            specialization=request.form.get('specialization'),
            experience=int(request.form.get('experience')),
            city=request.form.get('city'),
            fees=float(request.form.get('fees')),
            image=request.form.get('image', '/static/images/doctor1.jpg'),
            password_hash=generate_password_hash(request.form.get('password'))
        )
        
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor added successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_doctor.html')

@app.route('/admin/delete-doctor/<int:doctor_id>', methods=['POST'])
@admin_required
def delete_doctor(doctor_id):
    """Delete doctor from the system"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Delete associated appointments first
    Appointment.query.filter_by(doctor_id=doctor.id).delete()
    
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

# update


# Helper function to initialize the database with sample data
# def init_db():
#     """Initialize database with sample doctors"""
#     with app.app_context():
#         db.create_all()
        
#         # Check if we already have doctors
#         if Doctor.query.count() == 0:
#             # Sample specializations mapped to illnesses
#             specialization_map = {
#                 'Heart Disease': 'Cardiology',
#                 'Bone & Joint Problems': 'Orthopedics',
#                 'Neurological Issues': 'Neurology',
#                 'Skin Problems': 'Dermatology',
#                 'ENT Issues': 'ENT',
#                 'Eye Problems': 'Ophthalmology'
#             }
            
#             # Sample cities
#             cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
            
#             # Create sample doctors for each specialization in each city
#             doctor_id = 1
#             print("\nSample Doctor Credentials:")
#             print("---------------------------")
#             for city in cities:
#                 for illness, specialization in specialization_map.items():
#                     # Create 2 doctors per specialization per city
#                     for i in range(2):
#                         experience = 5 + (doctor_id % 15)  # Random experience between 5-19 years
#                         fees = 500 + (doctor_id % 10) * 100  # Fees between 500-1400
                        
#                         doctor_id_str = f'DOC{doctor_id}'
#                         doctor = Doctor(
#                             doctor_id=doctor_id_str,
#                             name=f'Dr. Example {doctor_id}',
#                             specialization=specialization,
#                             experience=experience,
#                             city=city,
#                             fees=fees,
#                             image=f'/static/images/doctor{1 + (doctor_id % 10)}.jpg',
#                             password_hash=generate_password_hash('doctor123')
#                         )
#                         db.session.add(doctor)
#                         print(f"Doctor ID: {doctor_id_str}, Password: doctor123")
#                         doctor_id += 1
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        if Admin.query.count() == 0:
            admin = Admin(
                username='admin',
                email='admin@cureclick.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()





# Helper function to initialize the database with sample data
def add_more_doctors():
    """Add more doctors to ensure at least 2 per specialization in each city"""
    with app.app_context():
        # Sample specializations mapped to illnesses
        specialization_map = {
            'Heart Disease': 'Cardiology',
            'Bone & Joint Problems': 'Orthopedics',
            'Neurological Issues': 'Neurology',
            'Skin Problems': 'Dermatology',
            'ENT Issues': 'ENT',
            'Eye Problems': 'Ophthalmology'
        }
        
        # Sample cities
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']
        
        # Sample first names and last names for more variety
        first_names = ['Aarav', 'Aditi', 'Arjun', 'Diya', 'Ishaan', 'Kavya', 'Neha', 'Rohan', 'Sanya', 'Vikram']
        last_names = ['Patel', 'Sharma', 'Singh', 'Gupta', 'Kumar', 'Reddy', 'Joshi', 'Malhotra', 'Kapoor', 'Verma']
        
        # Find the highest current doctor_id
        highest_id = 0
        doctors = Doctor.query.all()
        for doctor in doctors:
            try:
                # Extract numeric part of DOC1001, etc.
                doc_id = int(doctor.doctor_id[3:])
                if doc_id > highest_id:
                    highest_id = doc_id
            except:
                pass
        
        if highest_id == 0:
            highest_id = 1000  # Start at 1001 if no doctors exist
        
        doctor_id = highest_id + 1
        doctors_added = 0
        
        
        for city in cities:
            for illness, specialization in specialization_map.items():
                # Check how many doctors we already have for this specialization and city
                existing_count = Doctor.query.filter_by(
                    specialization=specialization,
                    city=city
                ).count()
                
                # Add doctors until we have at least 2
                doctors_to_add = max(0, 2 - existing_count)
                
                for i in range(doctors_to_add):
                    experience = 5 + (doctor_id % 20)  # Random experience between 5-24 years
                    fees = 500 + (doctor_id % 15) * 100  # Fees between 500-1900
                    
                    doctor_id_str = f'DOC{doctor_id}'
                    first_name = first_names[doctor_id % len(first_names)]
                    last_name = last_names[doctor_id % len(last_names)]
                    doctor = Doctor(
                        doctor_id=doctor_id_str,
                        name=f'Dr. {first_name} {last_name}',
                        specialization=specialization,
                        experience=experience,
                        city=city,
                        fees=fees,
                        image=f'/static/images/doctor{1 + (doctor_id % 10)}.jpg',
                        password_hash=generate_password_hash('doctor123')
                    )
                    db.session.add(doctor)
                    # print(f"Doctor ID: {doctor_id_str}, Name: Dr. {first_name} {last_name}, Specialization: {specialization}, City: {city}, Password: doctor123")
                    doctor_id += 1
                    doctors_added += 1
        
        db.session.commit()

# ... (rest of the code remains unchanged)

# ... (rest of the code remains unchanged)
            
        db.session.commit()

if __name__ == '__main__':
    # Initialize the database
    add_more_doctors()
    init_db()

    # Run the application in debug mode
    app.run(debug=True)