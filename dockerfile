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
# We're installing a mix of versions that should work together
RUN pip install --no-cache-dir runpod==1.5.0 && \
    pip install --no-cache-dir huggingface_hub==0.15.1 && \
    pip install --no-cache-dir tokenizers==0.13.3 && \
    pip install --no-cache-dir torch==2.1.0 && \
    pip install --no-cache-dir accelerate==0.27.2 && \
    pip install --no-cache-dir safetensors==0.4.2 && \
    pip install --no-cache-dir pillow==10.2.0 && \
    pip install --no-cache-dir sentencepiece && \
    pip install --no-cache-dir transformers==4.26.0 && \
    pip install --no-cache-dir "diffusers[torch]>=0.23.0"

# Copy handler script
COPY handler.py /app/handler.py

# Set Python path
ENV PYTHONPATH=/app

# Set environment variables for better performance
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE="/cache/huggingface"
ENV TORCH_HOME="/cache/torch"

# RunPod will automatically provide the HF_TOKEN env variable if set in the template
# The entrypoint to start the RunPod handler
CMD ["python", "-u", "handler.py"]