# 🚀 Field Worker CRM

A Django-based Field Worker CRM (Customer Relationship Management) system that helps organizations manage field workers, customers, attendance, tasks, visits, and notifications efficiently.

## 📌 Features

- 👤 User Authentication & Role Management
- 🏢 Customer Management
- 📋 Task Assignment
- 📍 Field Visit Tracking
- 🕒 Attendance Management
- 📝 Leave Management
- ⭐ Customer Feedback
- 📊 Dashboard & Analytics
- 📧 Email Notifications
- 🤖 AI Engine Integration (Groq API)

## 🛠️ Tech Stack

- Python
- Django
- HTML
- CSS
- Bootstrap
- SQLite
- JavaScript
- Groq API

## 📂 Project Structure

```
field_worker/
│── accounts/
│── ai_engine/
│── analytics/
│── api/
│── attendance/
│── customers/
│── dashboard/
│── feedbacks/
│── leaves/
│── notifications/
│── tasks/
│── visits/
│── templates/
│── static/
│── manage.py
```

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/G-Nishanthi21/Fieldworker-CRM.git
```

### Move to Project Folder

```bash
cd Fieldworker-CRM
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_groq_api_key
```

### Apply Migrations

```bash
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## 📷 Modules

- Authentication
- Customer Management
- Attendance
- Leave Management
- Task Management
- Visit Management
- Feedback System
- Notifications
- Dashboard
- AI Chatbot

---

## 📈 Future Enhancements

- GPS Tracking
- Mobile App Integration
- Report Generation (PDF/Excel)
- SMS Notifications
- Real-time Location Tracking
