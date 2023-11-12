# Use an official Python runtime as a parent image
FROM python:3.10-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the 'shivu' directory (assuming it's in the same directory as the Dockerfile)
COPY shivu /app/shivu

# Make port 80 available to the world outside this container
EXPOSE 80

# Run __main__.py when the container launches
CMD ["python3", "-m", "shivu"]
