FROM python:3.14.8-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY cyberlab/demo.py /app/demo.py
USER 10001:10001
EXPOSE 8080
CMD ["python", "/app/demo.py"]
