### CureClick - Doctor Appointment Booking System
CureClick is a Flask-based web application that allows patients to book doctor appointments seamlessly. It also provides a doctor login portal, where doctors can view and manage their scheduled appointments.

🚀 Features
For Patients
✅ Book Appointments – Select location, appointment type, and preferred doctor.
✅ View Available Slots – Choose from open time slots for appointments.


For Doctors
✅ Secure Login – Doctors can log in to view their appointments.
✅ Appointment Management – Doctors can see a list of their scheduled appointments.

## 🛠 Installation Guide
1️⃣ Clone the Repository
git clone <repository-url>
cd CureClick
2️⃣ Create a Virtual Environment (Optional, Recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3️⃣ Install Required Dependencies
pip install -r requirements.txt
4️⃣ Set Up the Database

flask db init
flask db migrate -m "Initial migration"
flask db upgrade
5️⃣ Run the Flask Application
py app.py
The application will be available at http://127.0.0.1:5000/.

📂 Project Structure
csharp
Copy
Edit
CureClick/
│── app.py/               # Main application files
│   ├── static/        # CSS, JavaScript, images
│   ├── templates/     # HTML templates
│── config.py          # Configuration settings
│── README.md          # Project documentation           
🎯 Usage Instructions
For Patients
1️⃣ Visit the website and select your location.
2️⃣ Choose the type of appointment (Check-up, Specialist, etc.).
3️⃣ Pick an available doctor and a time slot.
4️⃣ Confirm the appointment.

For Doctors
1️⃣ Log in using your doctor credentials.
2️⃣ View a list of scheduled appointments.
3️⃣ Manage and keep track of patient visits.

