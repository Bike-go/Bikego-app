# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable to avoid running Python in buffer mode
ENV PYTHONUNBUFFERED=1

# Run the schema upload script followed by the Flask app
CMD ["sh", "-c", "python upload_schema.py && python app.py"]