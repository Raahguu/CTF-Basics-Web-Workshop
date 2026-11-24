FROM python:3.13-alpine AS builder

WORKDIR /app

COPY . /app
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 80
CMD ["python3", "app.py"]
