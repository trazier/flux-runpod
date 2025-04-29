# FLUX.1 [dev] Serverless API for RunPod

This repository contains the necessary files to deploy the FLUX.1 [dev] image generation model as a serverless API on RunPod.

## What is FLUX.1 [dev]?

FLUX.1 [dev] is a 12 billion parameter rectified flow transformer developed by Black Forest Labs, capable of generating high-quality images from text descriptions. The model is designed for efficient image generation while providing competitive prompt following capability.

## Repository Contents

- `handler.py`: The main handler script that processes API requests and generates images
- `Dockerfile`: Container definition with all required dependencies
- `runpod-serverless.json`: Configuration file for RunPod Serverless

## Deployment Instructions

### Prerequisites

1. A RunPod account with billing set up
2. Access to GPUs with at least 24GB VRAM

### Steps

1. Clone this repository
2. Build the Docker image:
   ```bash
   docker build -t your-registry/flux1-dev:latest .
   ```
3. Push to your container registry:
   ```bash
   docker push your-registry/flux1-dev:latest
   ```
4. Create a new Serverless endpoint on RunPod:
   - Go to [RunPod Serverless Console](https://www.runpod.io/console/serverless)
   - Click "New Endpoint"
   - Select "Custom" template
   - Enter your Docker image URL
   - Configure GPU type (minimum 24GB VRAM)
   - Set the handler to: `/app/handler.py`
   - Create the endpoint

## API Usage

### Request Format

```json
{
  "input": {
    "prompt": "A cat holding a sign that says hello world",
    "height": 1024,
    "width": 1024,
    "guidance_scale": 3.5,
    "num_inference_steps": 50,
    "max_sequence_length": 512,
    "seed": null
  }
}
```

### Parameters

- `prompt` (required): Text description of the image you want to generate
- `height` (optional): Image height in pixels (default: 1024)
- `width` (optional): Image width in pixels (default: 1024)
- `guidance_scale` (optional): Controls how closely the image follows the prompt (default: 3.5)
- `num_inference_steps` (optional): Number of denoising steps, higher values give better quality but take longer (default: 50)
- `max_sequence_length` (optional): Maximum length of the input text (default: 512)
- `seed` (optional): Seed for reproducible generation, omit for random results

### Response Format

```json
{
  "image_base64": "base64_encoded_image_data",
  "generation_time": 10.5,
  "model_id": "black-forest-labs/FLUX.1-dev",
  "parameters": {
    "prompt": "A cat holding a sign that says hello world",
    "height": 1024,
    "width": 1024,
    "guidance_scale": 3.5,
    "num_inference_steps": 50,
    "max_sequence_length": 512,
    "seed": 42
  },
  "license": "FLUX.1 [dev] Non-Commercial License - outputs can be used for personal, scientific, and commercial purposes"
}
```

## Performance Considerations

- The model requires a GPU with at least 24GB of VRAM (NVIDIA RTX A5000, A6000, or better is recommended)
- First inference will be slower as the model needs to be loaded into memory
- Increasing `num_inference_steps` will produce higher quality images but will take longer to generate
- The `guidance_scale` parameter controls how closely the image follows the prompt (higher values = more prompt adherence)

## License

This implementation is provided for use with the FLUX.1 [dev] model, which is released under the FLUX.1 [dev] Non-Commercial License. The generated outputs can be used for personal, scientific, and commercial purposes as described in the license.

## Acknowledgments

- [Black Forest Labs](https://huggingface.co/black-forest-labs) for creating and sharing the FLUX.1 [dev] model
- [Hugging Face](https://huggingface.co/) for hosting the model and providing the diffusers library
- [RunPod](https://www.runpod.io/) for the serverless GPU infrastructure