# Use an official stable Python image (3.10 for compatibility with imghdr)
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot source files
COPY . .

# Set environment variables (OPTIONAL - You can also use Northflank's secrets)
# Note: Do NOT hardcode sensitive tokens in Dockerfile in production!
ENV TELEGRAM_BOT_TOKEN="your-token"

# Define start command
CMD ["python", "main.py"]