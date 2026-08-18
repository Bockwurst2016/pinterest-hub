import requests
import json
import logging
from typing import Dict, List
from src.core.config_loader import CONFIG

logger = logging.getLogger("TextEngine")

class TextEngine:
    def __init__(self):
        self.base_url = CONFIG['ollama']['base_url']
        self.model = CONFIG['ollama']['model']

    def generate_content(self, niche_data: Dict, product_data: Dict) -> Dict[str, str]:
        """
        Generates text content and an image prompt using Ollama.
        
        :param niche_data: Data from the Niches table (modifiers, audience).
        :param product_data: Data from the Products table (title, description, link).
        :return: Dictionary containing title, description, and image_prompt.
        """
        prompt = f"""
        You are a professional Pinterest content creator specializing in {niche_data['audience']}.
        The vibe should be: {niche_data['prompt_modifiers'].get('tone', 'engaging')}.
        Style: {niche_data['prompt_modifiers'].get('style', 'aesthetic')}.

        Product Details:
        Name: {product_data['title']}
        Description: {product_data['description']}
        Link: {product_data['amazon_link']}

        Task:
        1. Create a catchy, SEO-friendly Pinterest title (under 50 characters).
        2. Write a compelling description (under 300 characters) that encourages clicks. Include a Call to Action (CTA) to check the link in the bio/description.
        3. Create a detailed 'Image Generation Prompt' for a high-quality lifestyle image. 
           The image should be in a 2:3 aspect ratio and feel like a "cozy" lifestyle shot, not an ad.
           Focus on the atmosphere and the product's placement in a real-world setting.

        Return the result strictly in JSON format:
        {{
            "title": "...",
            "description": "...",
            "image_prompt": "..."
        }}
        """

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            
            # Ollama returns the JSON string in the 'response' field
            result = json.loads(response.json()['response'])
            logger.info(f"Successfully generated content for: {product_data['title']}")
            return result

        except Exception as e:
            logger.error(f"Error during Text Generation: {str(e)}")
            raise
