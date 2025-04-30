import os
import runpod
import torch
import shutil
import base64
from io import BytesIO

def handler(event):
    """
    Handler for image generation using Stable Diffusion.
    Since FLUX.1 has compatibility issues, we're using SD as an alternative.
    """
    try:
        # Get input parameters
        input_data = event.get("input", {})
        prompt = input_data.get("prompt", "A cat holding a sign that says hello world")
        height = input_data.get("height", 512)
        width = input_data.get("width", 512)
        num_inference_steps = input_data.get("num_inference_steps", 50)
        guidance_scale = input_data.get("guidance_scale", 7.5)
        seed = input_data.get("seed", None)
        
        # Print status to logs
        print(f"Loading model and generating image with prompt: {prompt}")
        
        # Import here to avoid initial errors
        from diffusers import StableDiffusionPipeline
        
        # Set up random seed if provided
        generator = None
        if seed is not None:
            generator = torch.Generator("cpu").manual_seed(seed)
        
        # Use SD XL Turbo for high quality, fast generation
        model_id = "stabilityai/sdxl-turbo" 
        
        # Initialize the model
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            cache_dir="/cache"
        )
        
        # Enable optimizations
        pipe.enable_attention_slicing()
        if hasattr(pipe, 'enable_model_cpu_offload'):
            pipe.enable_model_cpu_offload()
        
        # Generate image
        image = pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps if num_inference_steps <= 8 else 8,  # SDXL Turbo works best with 1-8 steps
            guidance_scale=guidance_scale,
            generator=generator
        ).images[0]
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Return result
        return {
            "status": "success",
            "image_base64": image_base64,
            "model_id": model_id,
            "prompt": prompt,
            "parameters": {
                "height": height,
                "width": width,
                "num_inference_steps": num_inference_steps if num_inference_steps <= 8 else 8,
                "guidance_scale": guidance_scale,
                "seed": seed
            },
            "note": "Used Stable Diffusion XL Turbo as FLUX.1 had compatibility issues"
        }
        
    except Exception as e:
        # Get error details
        import traceback
        error_details = traceback.format_exc()
        
        return {
            "status": "error",
            "error": str(e),
            "error_details": error_details
        }

# Start the serverless function
runpod.serverless.start({"handler": handler})