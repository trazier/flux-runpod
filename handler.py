import runpod
import sys

def handler(event):
    # Check for availability of required libraries
    libraries = {
        "diffusers": False,
        "torch": False
    }
    
    try:
        import diffusers
        libraries["diffusers"] = True
    except ImportError as e:
        libraries["diffusers"] = str(e)
        
    try:
        import torch
        libraries["torch"] = True
    except ImportError as e:
        libraries["torch"] = str(e)
    
    return {
        "status": "Library check completed",
        "libraries": libraries,
        "python_version": sys.version
    }

runpod.serverless.start({"handler": handler})