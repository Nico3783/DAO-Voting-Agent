# Using the official slim Python image for a smaller footprint
FROM python:3.11-slim

# Installing Git and essential build dependencies in one step to reduce Docker image layers
RUN apt-get update && \
    apt-get install -y git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Installing Rust, which is necessary for biscuit-python
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Setting up Rust environment variables for the build process
ENV PATH="/root/.cargo/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Setting the working directory
WORKDIR /app

# Copying the requirements file first to take advantage of Docker’s caching for dependencies
COPY requirements.txt .

# Installing Python dependencies from requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copying the rest of the application code to the container
COPY . .

# Exposing the port the app runs on
EXPOSE 8080

# Command to run the application using Gunicorn
CMD ["gunicorn", "src.app:app"]
