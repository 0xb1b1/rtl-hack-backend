FROM python:3.11

# Select working directory
WORKDIR /app

# Copy requirements.txt to working directory
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy required files to working directory
COPY server.py .
COPY modules/ ./modules/

# Create data directory
# RUN mkdir -p /data/logs

# Run the bot
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
