import runpod

def handler(event):
    return {"status": "success", "message": "Handler initialized successfully"}

runpod.serverless.start({"handler": handler})