# Real-Time Organizational Dashboard

A centralized, real-time dashboard platform for managing organizational operations, project tracking, and task allocations. Built with Django and MySQL/SQLite3, the system provides role-based access for Admins, Project Managers, and Employees, along with dynamic data visualizations and AI-powered chatbot support.

## 🚀 Features

- 🔒 **Role-Based Access Control** (Admin, Project Manager, Employee)
- 📊 **Real-Time Dashboards** using Chart.js
- 🤖 **AI Chatbot Integration** (role-specific query access)
- 🧩 **Modular Architecture** (Admin, PM, Employee modules)
- 📁 **Department & Project Management**
- ⏱️ **Task Allocation & Progress Tracking**
- 📈 **KPI Monitoring & Predictive Insights**
- 📱 **Flutter-based Android App (Optional)**

---

## 🛠️ Tech Stack

- **Framework:** Django
- **Databases:** MySQL (primary), SQLite3 (development/testing)
- **Frontend:** Django Templates (Web UI), Chart.js for visualization
- **Mobile App (Optional):** Flutter for Android
- **Authentication:** Django Auth with CSRF protection
- **Environment Config:** `.env` file for sensitive variables

---

## 📦 Project Structure

```bash
├── dashboard/              # Main Django app
├── templates/              # Frontend templates (HTML/CSS/JS)
├── static/                 # Static files (Chart.js, styles, scripts)
├── chatbot/                # AI Chatbot logic and integrations
├── db.sqlite3              # Default SQLite3 database (optional)
├── manage.py
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables

```
