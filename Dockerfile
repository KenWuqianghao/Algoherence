# Use a slim Python image for a smaller footprint
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/src

# Create and set the working directory
WORKDIR /app

# Install system dependencies (for building some Python packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the source code
COPY . .

# Copy requirements and install dependencies
RUN pip install --upgrade pip && \
    pip install .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "src/algoherence/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
