import logging
from typing import List
from PIL import Image
from src.core.config_loader import CONFIG
import os

logger = logging.getLogger("BrandingProcessor")

class BrandingProcessor:
    def __init__(self):
        self.logo_path = CONFIG['branding']['logo_path']
        self.watermark_path = CONFIG['branding']['watermark_path']

    def apply_branding(self, image_path: str) -> str:
        """
        Applies branding (logo and watermark) to the generated image.
        
        :param image_path: Path to the generated image.
        :return: Path to the branded image.
        """
        try:
            # Open the generated image
            img = Image.open(image_path).convert("RGBA")
            
            # Load assets
            if os.path.exists(self.logo_path):
                logo = Image.open(self.logo_path).convert("RGBA")
                # Resize logo (e.g., to 15% of image width)
                base_width = img.width
                logo_width = int(base_width * 0.15)
                w_ratio = logo_width / float(logo.size[0])
                logo_height = int(float(logo.size[1]) * float(w_ratio))
                logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                
                # Paste logo at bottom-right (with 20px padding)
                img.paste(logo, (img.width - logo.width - 20, img.height - logo.height - 20), logo)

            if os.path.exists(self.watermark_path):
                watermark = Image.open(self.watermark_path).convert("RGBA")
                # Simple resizing
                watermark = watermark.resize((200, 200), Image.Resampling.LANCZOS)
                # Paste watermark at top-left
                img.paste(watermark, (20, 20), watermark)

            # Save the final branded image
            branded_path = image_path.replace(".png", "_branded.png")
            img.convert("RGB").save(branded_path)
            logger.info(f"Branding applied: {branded_path}")
            return branded_path

        except Exception as e:
            logger.error(f"Error in BrandingProcessor: {str(e)}")
            raise
