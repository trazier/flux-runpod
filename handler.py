import os
import runpod
import torch
import shutil
import base64
from io import BytesIO
from diffusers import DiffusionPipeline

def handler(event):
    """
    Handler for image generation using DiffusionPipeline with FLUX.1 model.
    This attempts to use DiffusionPipeline as a generic wrapper to load FLUX.1.
    """
    try:
        # Check disk space first
        disk_info = {}
        for path in ["/", "/tmp", "/app", "/cache"]:
            try:
                if os.path.exists(path):
                    total, used, free = shutil.disk_usage(path)
                    disk_info[path] = {
                        "total_gb": round(total / (1024**3), 2),
                        "used_gb": round(used / (1024**3), 2),
                        "free_gb": round(free / (1024**3), 2)
                    }
            except Exception as e:
                disk_info[path] = f"Error checking: {str(e)}"
        
        # Get input parameters
        input_data = event.get("input", {})
        prompt = input_data.get("prompt", "A cat holding a sign that says hello world")
        height = input_data.get("height", 768)
        width = input_data.get("width", 768)
        num_inference_steps = input_data.get("num_inference_steps", 50)
        guidance_scale = input_data.get("guidance_scale", 3.5)
        seed = input_data.get("seed", None)
        
        # Set up random seed if provided
        generator = None
        if seed is not None:
            generator = torch.Generator("cpu").manual_seed(seed)
        
        # Make sure HF_TOKEN is set in environment
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            return {
                "status": "error",
                "error": "HF_TOKEN environment variable not set. Required for accessing FLUX.1 model."
            }
        
        # Try using DiffusionPipeline which can load various pipeline types
        print("Attempting to load FLUX.1-dev model...")
        model_id = "black-forest-labs/FLUX.1-dev"
        
        # Load the model using DiffusionPipeline which can adapt to various pipeline types
        pipe = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,  # Use float16 instead of bfloat16 for better compatibility
            cache_dir="/cache",         # Use the larger volume for caching
            token=hf_token             # Pass the HF token for gated model access
        )
        
        # Try to enable memory optimizations if available
        if hasattr(pipe, 'enable_attention_slicing'):
            pipe.enable_attention_slicing()
        if hasattr(pipe, 'enable_model_cpu_offload'):
            pipe.enable_model_cpu_offload()
        
        # Generate the image 
        print(f"Generating image with prompt: {prompt}")
        image = pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]
        
        # Convert image to base64 for API response
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Return the generated image and info
        return {
            "status": "success",
            "image_base64": image_base64,
            "model_id": model_id,
            "prompt": prompt,
            "parameters": {
                "height": height,
                "width": width,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "seed": seed
            }
        }
        
    except Exception as e:
        # Return detailed error for debugging
        return {
            "status": "error",
            "error": str(e),
            "disk_info": disk_info if 'disk_info' in locals() else "Not available"
        }

# Start the serverless function
runpod.serverless.start({"handler": handler})