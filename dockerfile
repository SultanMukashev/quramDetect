# Stage 1: Build stage (includes Python packages installation)
FROM python:3.12-slim as builder

# Set environment variables to improve runtime behavior
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the builder container
WORKDIR /app

# Copy only requirements for efficient caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the builder
COPY . .

# Stage 2: Runtime stage (lightweight image)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the runtime container
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /app /app

# Command to run your application
# CMD ["python"," /app/telegram_bot/aiogram_run.py"]
# CMD ["ls", "-la", "/app/telegram_bot"]
EXPOSE 5000
CMD ["python", "/app/detector.py"]

