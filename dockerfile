# Use the official slim version of the Python image based on Debian Bullseye
FROM python:3.11-slim-bullseye

# Set the working directory in the container to /app
WORKDIR /app

# Set PYTHONPATH environment variable
ENV PYTHONPATH=./src:$PYTHONPATH

# Copy the Python requirements file into the container at /app
COPY requirements.txt .

# Update the package list, install the necessary packages,
# then clean up to reduce the image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        git \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the Python dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools

# isntall streamlit
RUN pip install streamlit

# Install the requirements
RUN pip install --trusted-host pypi.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8501 used by streamlit
EXPOSE 8501

# Define the env variable for streamlit server
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Start a bash shell and source the CHATBOT_NAME value from /etc/bash.bashrc
CMD ["streamlit", "run", "/app/src/deployment/v1.py"]
