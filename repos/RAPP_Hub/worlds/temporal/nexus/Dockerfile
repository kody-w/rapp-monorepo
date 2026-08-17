# Nexus Dimension - Portable, self-contained
FROM python:3.11-slim

WORKDIR /dimension

# Install runtime
RUN pip install --no-cache-dir fastapi uvicorn[standard]

# Copy dimension (everything needed)
COPY . .

EXPOSE 8888

CMD ["python", "serve.py", "8888"]
