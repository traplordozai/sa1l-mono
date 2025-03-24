FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install python-dotenv
COPY . .
EXPOSE 8000
CMD ["gunicorn", "sail_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
