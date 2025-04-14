FROM python:3.13-alpine

WORKDIR /app

# Install ffmpeg and necessary libraries for Alpine
RUN apk update && apk add --no-cache ffmpeg libffi build-base

# Copy the requirements.txt first (to leverage Docker's cache)
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app

# Expose the port on which the application will run
EXPOSE 8000

# Run the main script with Uvicorn and reload option
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
