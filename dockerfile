# Using Ubuntu 23.04 as the base image
FROM python:3.11-slim-bullseye

# Set the working directory to /app
WORKDIR /app
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y --no-install-recommends --allow-change-held-packages \
        wget \
        python3-full \
        python3-pip \
        python3-dev \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --trusted-host pypi.org torch && \
    pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --trusted-host pypi.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "./src/streamlit_deployment/v0.py"]