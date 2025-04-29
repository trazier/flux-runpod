import os
import time
import json
import torch
import runpod
from diffusers import FluxPipeline

# Initialize model globally for reuse across requests
def initialize_model():
    model_id = os.environ.get("MODEL_ID", "black-forest-labs/FLUX.1-dev")
    
    print(f"Loading model: {model_id}")
    pipe = FluxPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16
    )
    
    # Enable model CPU offload to save VRAM if needed
    # Comment this out if you have sufficient GPU memory
    pipe.enable_model_cpu_offload()
    
    return pipe

# Initialize the model on startup
pipe = initialize_model()

def generate_image(prompt, height=1024, width=1024, guidance_scale=3.5, 
                  num_inference_steps=50, max_sequence_length=512, seed=None):
    """Generate an image based on text prompt using the loaded model"""
    
    # Set seed for reproducibility if provided
    generator = None
    if seed is not None:
        generator = torch.Generator("cpu").manual_seed(seed)
    
    # Record start time for performance tracking
    start_time = time.time()
    
    # Generate the image
    output = pipe(
        prompt,
        height=height,
        width=width,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        max_sequence_length=max_sequence_length,
        generator=generator
    )
    
    # Calculate time taken
    generation_time = time.time() - start_time
    
    # Convert image to base64 for API response
    import base64
    from io import BytesIO
    
    image = output.images[0]
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return {
        "image_base64": image_base64,
        "generation_time": generation_time,
        "model_id": os.environ.get("MODEL_ID", "black-forest-labs/FLUX.1-dev"),
        "parameters": {
            "prompt": prompt,
            "height": height,
            "width": width,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "max_sequence_length": max_sequence_length,
            "seed": seed
        },
        "license": "FLUX.1 [dev] Non-Commercial License - outputs can be used for personal, scientific, and commercial purposes"
    }

def handler(event):
    """
    Handler function that processes the incoming API request for image generation.
    Expected input format:
    {
        "prompt": "Your text prompt here",
        "height": 1024,               # optional, defaults to 1024
        "width": 1024,                # optional, defaults to 1024
        "guidance_scale": 3.5,        # optional, defaults to 3.5
        "num_inference_steps": 50,    # optional, defaults to 50
        "max_sequence_length": 512,   # optional, defaults to 512
        "seed": null                  # optional, random seed if not provided
    }
    """
    try:
        # Extract input data
        input_data = event["input"]
        prompt = input_data.get("prompt")
        
        if not prompt:
            return {
                "error": "No prompt provided in the request"
            }
            
        # Get optional parameters
        height = input_data.get("height", 1024)
        width = input_data.get("width", 1024)
        guidance_scale = input_data.get("guidance_scale", 3.5)
        num_inference_steps = input_data.get("num_inference_steps", 50)
        max_sequence_length = input_data.get("max_sequence_length", 512)
        seed = input_data.get("seed")
        
        # Generate the image
        result = generate_image(
            prompt=prompt,
            height=height,
            width=width,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
            seed=seed
        )
        
        return result
        
    except Exception as e:
        # Return error message if anything goes wrong
        return {
            "error": str(e)
        }

# Start the serverless function
runpod.serverless.start({"handler": handler})