# -------------------------------
# Django Backend Dockerfile
# -------------------------------

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy the requirements file (we will create it later)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Set the default command (will be updated later)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
