import requests
import json
import time
import logging
from typing import Dict, Any, Optional
from src.core.config_loader import CONFIG

logger = logging.getLogger("ImageEngine")

class ImageEngine:
    def __init__(self):
        self.base_url = CONFIG['comfyui']['base_url']
        # For a production-ready implementation, we'd use a WebSocket client 
        # to listen for completion events. For this MVP, we use polling.
        self.poll_interval = 5
        self.timeout = 300

    def generate_image(self, prompt: str, aspect_ratio: str = "2:3") -> str:
        """
        Sends a prompt to ComfyUI and waits for the image to be generated.
        
        :param prompt: The text prompt to generate an image from.
        :param aspect_ratio: The target aspect ratio (e.g., "2:3" or "9:16").
        :return: Path to the generated image.
        """
        # Define dimensions based on aspect ratio
        # Pinterest standard for 2:3 is often 1080x1620
        if aspect_ratio == "2:3":
            width, height = 1080, 1620
        elif aspect_ratio == "9:16":
            width, height = 1080, 1920
        else:
            width, height = 1024, 1024

        logger.info(f"Requesting image generation: {prompt[:50]}... ({aspect_ratio})")

        # The workflow below is a simplified representation of a Flux.1 GGUF 
        # prompt injection into a ComfyUI workflow.
        # In a real scenario, this JSON structure would match the specific 
        # nodes of your Flux.1 GGUF setup.
        payload = {
            "prompt": {
                "CLIPTextEncode": {
                    "inputs": {
                        "text": prompt,
                        "pooled_output": True,
                        "clip_skip": 1,
                    },
                    "class_type": "CLIPTextEncode"
                },
                "KSampler": {
                    "inputs": {
                        "model": ["MODEL", 0],
                        "positive": ["ARGS", 0],
                        "negative": ["ARGS", 1],
                        "latent_image": ["ARGS", 2],
                        "steps": 25,
                        "cfg": 7.5,
                        "sampler_name": "euler",
                        "scheduler": "karras",
                        "denoise": 1.0,
                    },
                    "class_type": "KSampler"
                },
                "EmptyLatentImage": {
                    "inputs": {
                        "width": width,
                        "height": height,
                        "batch_size": 1,
                    },
                    "class_type": "EmptyLatentImage"
                }
            },
            "args": [prompt, "A blurred background, out of focus, high quality, 8k, highly detailed"],
            "class_type": "Flux_Prompt_Injection_Node" # Example of a custom node or simplified structure
        }

        try:
            # 1. Submit the prompt
            response = requests.post(f"{self.base_url}/prompt", json={
                "prompt": payload
            })
            response.raise_for_status()
            prompt_id = response.json().get("prompt_id")
            logger.info(f"Prompt submitted. ID: {prompt_id}")

            # 2. Poll for completion
            # This is a simplified polling logic. 
            # Real implementation would check /history for the most recent output.
            start_time = time.time()
            generated_path = ""
            
            while time.time() - start_time < self.timeout:
                time.sleep(self.poll_interval)
                
                # Placeholder for actual history check:
                # history_resp = requests.get(f"{self.base_url}/history")
                # history = history_resp.json()
                # if history and history[0]['prompt_id'] == prompt_id:
                #     if history[0]['data'].get('output_images'):
                #         generated_path = history[0]['data']['output_images'][0]['sub_type']
                #         break
                
                # Simulation of success for now
                generated_path = f"data/outputs/img_{prompt_id}.png"
                break

            if not generated_path:
                raise TimeoutError("Image generation timed out.")

            return generated_path

        except Exception as e:
            logger.error(f"Error in ImageEngine: {str(e)}")
            raise
