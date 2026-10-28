# Use the official Python 3.12 image built on Debian
FROM python:3.12-slim

# Set environment variables to avoid python generating .pyc files and to enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a user to avoid running the container as root
# HuggingFace spaces demand using a non-root user (id 1000)
RUN useradd -m -u 1000 user

# Set the working directory to the user's home directory
WORKDIR /home/user/app

# Change ownership of the app directory to the user
RUN chown user:user /home/user/app

# Switch to the non-root user
USER user

# Set PATH to include binaries installed via pip
ENV PATH="/home/user/.local/bin:$PATH"

# Copy the requirements file and install dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project context into the container
COPY --chown=user:user . .

# Expose the port that HuggingFace Spaces uses for Streamlit
EXPOSE 7860

# Install system dependencies needed for git-lfs fetching
USER root
RUN apt-get update && apt-get install -y git git-lfs && rm -rf /var/lib/apt/lists/*
USER user

# Define a startup script inline that pulls LFS files, then runs gunicorn
CMD ["sh", "-c", "git lfs install && git lfs pull && python -m gunicorn --bind 0.0.0.0:7860 src.app:app"]
