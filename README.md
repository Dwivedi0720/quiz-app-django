# 🎓 Role-Based Online Quiz & Student Performance Tracking System

A comprehensive Django-based quiz management system with role-based access control, timed quizzes, and detailed performance analytics.

## ✨ Features

### 👨‍🎓 Student Features
- **Take Timed Quizzes**: Each question has individual time limits
- **Instant Results**: View scores and correct answers after submission
- **Performance Dashboard**: Track daily and overall progress
- **Performance Analytics**: Visualize improvement with charts
- **One Attempt Policy**: Each quiz can only be attempted once

### 👨‍🏫 Trainer Features
- **Create & Manage Quizzes**: Full CRUD operations for quizzes
- **Question Management**: Add questions with time limits and explanations
- **Student Management**: Assign and activate/deactivate students
- **Performance Monitoring**: View individual student progress
- **Access Control**: Manage student access to the system

### 👨‍💼 Admin Features
- **Complete System Control**: Manage all users, quizzes, and data
- **User Management**: Create and manage trainers and students
- **System Analytics**: Overview of entire system performance

## 🚀 Quick Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Create Project Directory**
```bash
mkdir quiz_system
cd quiz_system
```

2. **Create Virtual Environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

3. **Install Django**
```bash
pip install django pillow
```

4. **Create Django Project**
```bash
django-admin startproject quiz_project .
```

5. **Create Apps**
```bash
python manage.py startapp accounts
python manage.py startapp quiz
python manage.py startapp progress
python manage.py startapp trainer
```

6. **Create Required Directories**
```bash
mkdir templates
mkdir templates/accounts
mkdir templates/quiz
mkdir templates/progress
mkdir templates/trainer
mkdir static
mkdir static/css
mkdir static/js
```

7. **Copy All Files**
   - Copy all provided code files to their respective locations
   - Make sure file names and locations match the structure shown

8. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

9. **Create Superuser (Admin)**
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

10. **Run Development Server**
```bash
python manage.py runserver
```

11. **Access the Application**
   - Open browser: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 📁 Project Structure

```
quiz_system/
├── manage.py
├── db.sqlite3
├── quiz_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── models.py (User profiles)
│   ├── views.py (Authentication)
│   ├── forms.py (Registration forms)
│   ├── urls.py
│   └── admin.py
├── quiz/
│   ├── models.py (Quiz, Question, Attempt)
│   ├── views.py (Quiz taking logic)
│   ├── urls.py
│   └── admin.py
├── progress/
│   ├── models.py (Daily/Overall progress)
│   ├── views.py (Dashboard)
│   ├── urls.py
│   └── admin.py
├── trainer/
│   ├── views.py (Trainer dashboard)
│   ├── forms.py (Quiz creation)
│   ├── urls.py
│   └── admin.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   ├── quiz/
│   ├── progress/
│   └── trainer/
└── static/
    ├── css/style.css
    └── js/quiz.js
```

## 🎯 How to Use

### For Students
1. Register as a student
2. Wait for trainer to activate your account
3. Browse available quizzes
4. Take quizzes (remember: one attempt only!)
5. View results and correct answers
6. Track your progress on the dashboard

### For Trainers
1. Register as a trainer
2. Create quizzes with questions
3. Assign students to your account
4. Activate/deactivate students
5. Monitor student performance
6. View detailed analytics

### For Admins
1. Log in to admin panel
2. Manage all users (students/trainers)
3. View all quizzes and attempts
4. Monitor system-wide statistics

## 🔐 Default Roles

- **Superuser (is_superuser=True)**: Full admin access
- **Trainer (is_staff=True)**: Can create quizzes and manage students
- **Student (normal user)**: Can take quizzes and view progress

## 📊 Database Models

### Key Models
- **User**: Django's default user model
- **StudentProfile**: Student details and status
- **TrainerProfile**: Trainer information
- **Quiz**: Quiz metadata and settings
- **Question**: Individual questions with options
- **QuizAttempt**: Student quiz attempts
- **StudentAnswer**: Individual question answers
- **DailyProgress**: Daily performance tracking
- **OverallProgress**: Cumulative statistics

## 🎨 Design Features

- **Modern UI**: Gradient backgrounds, smooth animations
- **Responsive Design**: Works on all devices
- **Interactive Elements**: Hover effects, transitions
- **Real-time Timers**: Question and overall quiz timers
- **Progress Tracking**: Visual progress bars and charts
- **Color-coded Results**: Green for correct, red for incorrect

## 🔧 Configuration

### Important Settings (settings.py)
```python
# Remember to change in production
SECRET_KEY = 'your-secret-key-here'
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
```

### Database
- Default: SQLite (included)
- Can be configured for PostgreSQL, MySQL

## 🐛 Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   pip install django pillow
   ```

2. **Migration errors**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Static files not loading**
   ```bash
   python manage.py collectstatic
   ```

4. **Permission denied errors**
   - Make sure you have write permissions
   - Run terminal as administrator (Windows)

## 📝 Interview Talking Points

**Project Overview:**
"I built a role-based Django quiz system with three user types: Admin, Trainer, and Student. The system features timed quizzes where each question has its own time limit, automatic performance tracking, and comprehensive analytics."

**Key Technical Features:**
- Role-based access control using Django's authentication
- Real-time JavaScript timers for quiz questions
- Signal-based automatic progress tracking
- AJAX for seamless answer submission
- Responsive CSS with modern design patterns
- One-attempt policy enforced at database level

**Architecture:**
- Modular app structure (accounts, quiz, progress, trainer)
- Model relationships with foreign keys and signals
- Form validation and security measures
- RESTful URL patterns

## 🚀 Future Enhancements

- Email notifications for quiz results
- Bulk question import from CSV
- Quiz categories and tags
- Difficulty-based question pools
- Mobile app integration
- Real-time leaderboards
- Certificate generation

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Developer

Created as a placement-ready project demonstrating:
- Django framework expertise
- Database design and ORM
- User authentication and authorization
- Frontend development (HTML/CSS/JS)
- Full-stack development skills

---

**Note**: This is a complete, production-ready codebase. All features are fully functional and tested. Simply copy-paste the code and follow the setup instructions.