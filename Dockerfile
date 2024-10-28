# Starting with an official Python image that has Ubuntu as its base
FROM python:3.11-slim

# Installing Rust and build dependencies for biscuit-python
RUN apt-get update && \
    apt-get install -y curl build-essential && \
    curl https://sh.rustup.rs -sSf | sh -s -- -y

# Setting environment variables for Rust and Python
ENV PATH="/root/.cargo/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Setting up the working directory
WORKDIR /app

# Copying the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copying the entire project into the working directory
COPY . .

# Exposing the port used by the Flask app (8080) in app.py under the src/ directory
EXPOSE 8080

# And lastly specifying the command to run the application
CMD CMD ["gunicorn", "app:app"]
