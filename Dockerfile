# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install poppler-utils for PDF processing
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install any required dependencies
RUN pip install --upgrade pip 
RUN pip3 install -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8080

# Define the command to run the application (replace "app" with your FastAPI app filename)
CMD ["python", "app.py"]