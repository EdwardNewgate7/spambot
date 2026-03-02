FROM python:3.10-slim

WORKDIR /app

# Install git if needed (some pip packages might need it)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "Kingbot.py"]
