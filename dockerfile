FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy semua file
COPY . .

# Expose port
EXPOSE 8080

# Jalankan bot (ganti dari python bot.py)
CMD ["python", "main.py"]