# 🅿️ Smart Parking System

An intelligent parking detection system powered by **YOLOv8**, **Django**, and **Docker**.  
It automatically detects **empty** and **occupied** parking spaces using the **PKLot dataset**,  
and includes a **Raspberry Pi simulator** for sending images to the backend API.

---

## 🚀 Quick Start

Follow these 5 steps to get the system running:

```bash
# 1️⃣ Clone the repository
git clone the Repository
cd SmartParkingSystem

# 2️⃣ Add your trained YOLOv8 model
# Place 'best.pt' inside backend/models/
# (file ignored by Git)
# e.g., backend/models/best.pt

# 3️⃣ Build and start the containers
docker compose up --build

# 4️⃣ Apply Django migrations (in container)
docker exec -it smartparkingsystem-backend-1 python manage.py migrate

# 5️⃣ Test the API comment in method_decorator in api/views.py
curl -X POST -F "image=@data/datasets/PKLot/valid/images/2013-04-13_14_55_09.jpg" \
http://localhost:8000/api/upload-image/
