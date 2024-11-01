# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install pip-tools to compile requirements.in
RUN pip install --no-cache-dir pip-tools

# Compile requirements.in into requirements.txt
RUN pip-compile requirements.in

# Install the packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sync/Remove all dependencies
RUN pip-sync

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run Streamlit when the container launches
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.headless=true"]
