FROM python:3.11

WORKDIR /testeOrchestrator

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Flask port
EXPOSE 5000

# Env
ENV FLASK_APP=testeOrchestrator.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production


CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "testeOrchestrator:testeOrchestrator"]
