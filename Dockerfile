FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall python-telegram-bot==20.8

COPY . .

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]