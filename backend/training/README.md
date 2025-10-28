# 🅿️ Smart Parking System

An intelligent parking detection system powered by **YOLOv8**, **Django**, and **Docker**.  
It automatically detects **empty** and **occupied** parking spots using images from the **PKLot dataset**,  
and includes a **Raspberry Pi simulator** that uploads images to the backend API.

---
⚙️ Prerequisites

Make sure you have installed:

| Tool | Version |
|------|----------|
| 🐳 Docker | 24+ |
| 🐍 Python | 3.11+ |
| 🐙 Git | Latest |

---

📦 Setup Instructions

1️⃣ Clone the repositor

git clone the repo
cd SmartParkingSystem

2️⃣ Add YOLOv8 model
Place your trained best.pt file in:
backend/models/best.pt

3️⃣ Add dataset (optional for local testing)
data/datasets/PKLot/

Expected structure:
data/datasets/PKLot/
├── train/
├── valid/
└── test/

4️⃣ Build and start with Docker
docker compose up --build

This will start:
Django backend
PostgreSQL database
MinIO storage

Once running, access the API at:
👉 http://localhost:8000/api/upload-image/

5️⃣ Apply migrations (inside backend container)
docker exec -it smartparkingsystem-backend-1 python manage.py migrate

