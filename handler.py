import runpod
import os

def handler(event):
    """
    Simple handler function that checks for Hugging Face token
    and returns environment information.
    """
    # Check if HF_TOKEN is set
    hf_token = os.environ.get("HF_TOKEN", None)
    
    return {
        "status": "success",
        "hf_token_available": hf_token is not None,
        "message": "Handler initialized successfully. HF token status is shown above."
    }

# Start the serverless function
runpod.serverless.start({"handler": handler})