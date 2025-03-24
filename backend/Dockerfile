# Install python-dotenv
RUN pip install python-dotenv
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 8000
CMD ["gunicorn", "sail_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
