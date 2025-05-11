FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code and scripts
COPY . .

# Ensure start.sh is executable
RUN chmod +x start.sh

CMD ["./start.sh"]