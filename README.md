#  Rakmedia Task Management API

A **Django REST Framework**-based backend for managing employees, departments, and tasks within an organization.  
Managers can assign tasks, upload related files, mark tasks as complete, and employees can view their assigned tasks, as well as upload files related to each task which managers can then download. 

This project includes **role-based permissions**, **caching**, **file uploads**, and **asynchronous email notifications** using **Django Q2**.

I've created a basic frontend UI using React.js styled with TailwindCSS, just to test out different features of the application.
The backend application is fully customizable, scalable, and can be integrated with any kind of frontend UI.
---

##  Features

###  Authentication & Users
- JWT-based authentication (`djangorestframework-simplejwt`)
- Custom `User` model integrated with `Employee` and `Department` models
- Role-based permissions (Manager vs Employee)

###  Task Management
- Managers can:
  - Assign tasks to employees
  - Upload/delete files for tasks
  - Mark tasks as complete/incomplete
- Employees can view their tasks and files

###  Smart Caching
- Custom reusable decorator `@cache_response("cache_key")`
- Automatic cache invalidation on `post_save`, `post_delete`, and `m2m_changed`
- File upload/delete triggers cache invalidation (via signals)

###  Background Email Notifications
- Automatic email sent to new employees with username and password
- Powered by **Django Q2** for background processing
- Supports `console`, `SMTP`, or any email backend

###  Environment-Based Settings
- Three-tier configuration using:
  - `base.py` (shared)
  - `dev.py`
  - `prod.py`
- Environment variables loaded from `.env`

###  File Management
- File uploads linked to tasks
- Secure permission checks (employees can delete only their own files)

---

##  Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend Framework** | Django 5.x |
| **API Framework** | Django REST Framework |
| **Auth** | SimpleJWT |
| **Caching** | Redis / LocMemCache |
| **Async Tasks** | Django Q2 |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) |
| **Environment Config** | python-dotenv |
| **File Storage** | Django File Storage API |

---


