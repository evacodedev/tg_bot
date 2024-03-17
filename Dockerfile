FROM python:3.10.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
WORKDIR /app/src
CMD ["python", "app.py"]