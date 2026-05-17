# Use a clean, official light Python image
FROM python:3.10-slim

# Install system dependencies needed for compiling math libraries like FAISS and parsing PDFs
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container to /code
WORKDIR /code

# Copy the requirements file first to take advantage of Docker layer caching
COPY ./requirements.txt /code/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the backend files into the container
COPY . /code

# Pre-create the directory structure for indexes, chunks, and uploads
RUN mkdir -p /code/storage/indices /code/storage/chunks /code/uploads

# Expose port 7860 (Hugging Face Spaces requirement)
EXPOSE 7860

# Start the FastAPI application with Uvicorn on port 7860
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
