import runpod
from diffusers import FluxPipeline  # Just add the import, don't initialize

def handler(event):
    return {"status": "success", "message": "Import successful"}

runpod.serverless.start({"handler": handler})