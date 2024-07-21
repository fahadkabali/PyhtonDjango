CSAT Tool
Overview
The CSAT (Cyber Security Awareness Tool) is a Django-based web application designed to assess and improve staff awareness in cybersecurity. It features user authentication, dynamic assessment forms, score calculation, and personalized recommendations based on user responses.

Features
User authentication and profile management
Dynamic assessment forms with single-choice and multiple-choice questions
Score calculation and result categorization (Advanced, Average, Basic, Weak)
Personalized recommendations based on assessment results
Restriction to ensure users can only submit the assessment once
Reset functionality for the assessment form
Installation
Prerequisites
Python 3.x
Django 4.x or above
pip (Python package installer)
Clone the Repository
bash
Copy code
git clone https://github.com/yourusername/csat-tool.git
cd csat-tool
Create a Virtual Environment
bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install Dependencies
bash
Copy code
pip install -r requirements.txt
Run Migrations
bash
Copy code
python manage.py migrate
Create a Superuser
bash
Copy code
python manage.py createsuperuser
Run the Development Server
bash
Copy code
python manage.py runserver
Open your browser and go to http://127.0.0.1:8000 to access the application.

Usage
Authentication
Register a new account or log in with an existing account.
Navigate to the profile page to update user information.
Taking an Assessment
After logging in, go to the assessment page.
Answer all questions in the assessment form.
Submit the form to get the results and recommendations.
The form can only be submitted once unless reset.
Viewing Results
After submitting the assessment, view the categorized results (Advanced, Average, Basic, Weak) and personalized recommendations.
Resetting the Form
Use the reset button to clear the form and allow a new submission.
Project Structure
Copy code
csat-tool/
├── CSAT/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
├── authentication/
│   ├── templates/
│   ├── views.py
│   ├── forms.py
│   └── ...
├── home/
│   ├── templates/
│   ├── views.py
│   ├── models.py
│   └── ...
├── manage.py
├── requirements.txt
└── README.md