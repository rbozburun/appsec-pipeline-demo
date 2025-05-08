FROM python:3.13-rc-slim

WORKDIR /app

COPY app/ /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]
