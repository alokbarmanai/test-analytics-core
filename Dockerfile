# Use an official lightweight Python runtime environment
FROM python:3.11-slim

# Set the working directory inside the container image layout
WORKDIR /app

# Copy the dependency configuration files first to utilize Docker's layer caching
COPY requirements.txt .

# Install dependencies directly into the container system layout
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project root layout into the container workdir
COPY . .

# Expose port 8000 to allow traffic to flow to your FastAPI server
EXPOSE 8000

# Command to launch the Uvicorn application server inside the container
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

