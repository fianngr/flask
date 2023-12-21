# Use the official Python image as a base image
FROM python:3.10-slim


ENV PYTHONUNBUFFERED TRUE
# Set the working directory in the container
ENV APP_HOME /app
WORKDIR $APP_HOME
# Install build dependencies
RUN apt-get update && \
    apt-get install -y build-essential libmariadb-dev-compat libmariadb-dev pkg-config
COPY . ./

# Copy the requirements file into the container at /app
# COPY requirements.txt /app/

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
# EXPOSE 5000
# Cleanup
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Expose the port that the app will run on


# Define environment variable for Flask


# Command to run on container start
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
