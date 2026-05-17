FROM python:3.10-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements with no-cache to keep build extremely fast
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire codebase (including FAISS index data)
COPY . .

# Expose the default port for Hugging Face Spaces
EXPOSE 7860

# Run uvicorn on port 7860
CMD ["uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "7860"]
