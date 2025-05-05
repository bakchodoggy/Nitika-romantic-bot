# Use official Python image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot source files
COPY . .

# Set environment variables (OPTIONAL - You can also use Northflank's secrets)
ENV TELEGRAM_BOT_TOKEN="your-token"

# Define start command
CMD ["python", "main.py"]
