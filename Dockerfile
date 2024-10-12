# Use the official Python 3.9 image as the base
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

# Expose port 80 for the application
EXPOSE 80

# Run the application using uvicorn, which is recommended for async frameworks like FastAPI
# If using Flask, you can switch this to ["python", "app.py"] and ensure app.py runs on port 80
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
