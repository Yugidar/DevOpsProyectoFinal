# Use a lightweight Python image as the base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy all application files to the container
COPY . /app

# Install required Python dependencies
RUN pip install --no-cache-dir pymysql flask requests beautifulsoup4

# Expose port 5000 for the Flask application
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "prueba.py"]
