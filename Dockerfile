# Use official Python image as base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container and install dependencies
COPY src/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app folder into the container
COPY src /app/src

# Expose the FastAPI default port
EXPOSE 8000
EXPOSE 8001

# Start both the HTTP server for frontend and FastAPI backend
CMD ["sh", "-c", "cd /app/src/frontend && python3 -m http.server 8001 & cd /app && uvicorn src.backend.doc_api:app --host 0.0.0.0 --port 8000"]
