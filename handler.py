import os
import runpod
import torch
import shutil

def handler(event):
    """
    Simple handler function for diagnosis without trying to use the FluxPipeline.
    """
    try:
        # Check disk space
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
        
        # Try to import diffusers just to test if it works
        import_info = {}
        try:
            import diffusers
            import_info["diffusers"] = f"Successfully imported version {diffusers.__version__}"
        except Exception as e:
            import_info["diffusers"] = f"Error: {str(e)}"
            
        try:
            import huggingface_hub
            import_info["huggingface_hub"] = f"Successfully imported version {huggingface_hub.__version__}"
        except Exception as e:
            import_info["huggingface_hub"] = f"Error: {str(e)}"
            
        try:
            import transformers
            import_info["transformers"] = f"Successfully imported version {transformers.__version__}"
        except Exception as e:
            import_info["transformers"] = f"Error: {str(e)}"
            
        # Return diagnostic info
        return {
            "status": "success",
            "message": "Handler executed without trying to load model yet",
            "disk_info": disk_info,
            "import_info": import_info,
            "prompt": prompt
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