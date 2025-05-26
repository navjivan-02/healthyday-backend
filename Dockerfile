# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy requirement files and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Set the Flask app environment variable
ENV FLASK_APP=app.py

# Run the Flask app on port 8080 (Cloud Run requirement)
CMD ["python", "app.py"]
