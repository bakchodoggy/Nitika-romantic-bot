# Use an official stable Python image (e.g., Python 3.10 for compatibility)
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Force reinstallation to ensure correct library version
RUN pip install --force-reinstall python-telegram-bot==20.8

# Copy bot source files
COPY . .

# Set environment variables (OPTIONAL - You can also use Northflank's secrets)
ENV TELEGRAM_BOT_TOKEN="your-token"

# Define start command
CMD ["python", "main.py"]