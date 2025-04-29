FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Set working directory
WORKDIR /app

# Set noninteractive to avoid tzdata and other prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in specific order to manage compatibility
RUN pip install --no-cache-dir runpod==1.5.0 && \
    pip install --no-cache-dir huggingface_hub==0.20.2 && \
    pip install --no-cache-dir torch==2.1.0 && \
    pip install --no-cache-dir accelerate==0.27.2 && \
    pip install --no-cache-dir safetensors==0.4.2 && \
    pip install --no-cache-dir pillow==10.2.0 && \
    pip install --no-cache-dir transformers==4.37.2 && \
    pip install --no-cache-dir diffusers==0.30.0

# Copy handler script
COPY handler.py /app/handler.py

# Set Python path
ENV PYTHONPATH=/app

# Set environment variables for better performance
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE="/cache/huggingface"
ENV TORCH_HOME="/cache/torch"

# RunPod will automatically provide the MODEL_ID env variable if set in the template
# But we'll set a default just in case
ENV MODEL_ID="black-forest-labs/FLUX.1-dev"

# The entrypoint to start the RunPod handler
CMD ["python", "-u", "handler.py"]