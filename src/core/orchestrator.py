import time
import logging
import json
from typing import List, Dict
from src.core.db_manager import DatabaseManager
from src.core.config_loader import CONFIG
from src.miners.mock_miner import MockTrendMiner
from src.generators.text_engine import TextEngine
from src.generators.image_engine import ImageEngine
from src.processors.branding_processor import BrandingProcessor

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()]
)
logger = logging.getLogger("Orchestrator")

class PipelineOrchestrator:
    def __init__(self):
        self.db = DatabaseManager(CONFIG['db_path'])
        self.trend_miner = MockTrendMiner()
        self.text_engine = TextEngine()
        self.image_engine = ImageEngine()
        self.branding_processor = BrandingProcessor()
        logger.info("Pipeline Orchestrator Initialized")

    def run_trend_mining(self):
        """
        Initial discovery phase: Populates Trends and Products.
        """
        logger.info("Starting Trend Mining Phase...")
        trends = self.trend_miner.fetch_trends()
        
        for trend in trends:
            keyword = trend['keyword']
            source = trend['source']
            confidence = trend['confidence_score']
            
            # 1. Create a Niche (or find an existing one)
            # For MVP, we use a dummy niche for the keywords
            niche_id = self.db.insert_niche("Home & Tech", {"tone": "aesthetic"}, "General")
            
            # 2. Insert Trend
            trend_id = self.db.insert_trend(niche_id, source, keyword, confidence)
            logger.info(f"Added Trend: {keyword} (Trend ID: {trend_id})")
            
            # 3. Extract and Insert Products
            products = self.trend_miner.extract_products(keyword)
            for prod in products:
                product_id = self.db.insert_product(trend_id, prod['title'], prod['description'], prod['amazon_link'])
                
                # Add to the work queue
                cursor = self.db.conn.cursor()
                cursor.execute("""
                    INSERT INTO Content_Queue (product_id, status)
                    VALUES (?, 'queued')
                """, (product_id,))
                self.db.conn.commit()
                logger.info(f"Added Product to queue: {prod['title']} (Product ID: {product_id})")
        
        logger.info("Trend Mining Phase Complete.")

    def run_pipeline(self):
        """
        The main loop that processes the Content_Queue.
        """
        logger.info("Starting Pipeline Execution Loop...")
        while True:
            queued_items = self.db.get_queued_content()
            if not queued_items:
                logger.info("No items in queue. Sleeping for 60s...")
                time.sleep(60)
                continue
            
            for item in queued_items:
                self.process_item(item)
            
            time.sleep(10)

    def process_item(self, item: Dict):
        content_id = item['id']
        logger.info(f"Processing item {content_id} (Status: {item['status']})")
        
        try:
            # 1. Text Generation Phase (Ollama)
            if item['status'] == 'queued':
                logger.info("Entering Text Generation Phase...")
                
                # Mocking data fetch for MVP (Replace with real DB queries for Niche/Product data)
                mock_niche = {"audience": "Home Decor", "prompt_modifiers": {"tone": "aesthetic", "style": "minimalist"}}
                mock_product = {"title": "Cozy Blanket", "description": "Soft and warm", "amazon_link": "https://amazon.com/test"}
                
                content_result = self.text_engine.generate_content(mock_niche, mock_product)
                
                # Update DB
                self.db.update_status(
                    content_id, 
                    'text_gen', 
                    text_content=json.dumps(content_result)
                )
                
            # 2. Image Generation Phase (ComfyUI)
            elif item['status'] == 'text_gen':
                logger.info("Entering Image Generation Phase...")
                
                content_data = json.loads(item['text_content'])
                
                # Generate image using the prompt from text engine
                image_path = self.image_engine.generate_image(
                    prompt=content_data.get('image_prompt', 'A cozy living room with aesthetic decor'),
                    aspect_ratio="2:3"
                )
                
                self.db.update_status(content_id, 'image_gen', image_path=image_path)
                
            # 3. Branding Phase
            elif item['status'] == 'image_gen':
                logger.info("Entering Branding Phase...")
                
                branded_path = self.branding_processor.apply_branding(item['image_path'])
                
                self.db.update_status(content_id, 'branding', image_path=branded_path)
                
            # 4. Publication Phase
            elif item['status'] == 'branding':
                logger.info("Entering Distribution Phase...")
                
                # Placeholder for Pinterest Posting
                # self.distributor.post_to_pinterest(...)
                
                self.db.update_status(content_id, 'published')
                logger.info(f"Successfully published content {content_id}")

        except Exception as e:
            logger.error(f"Error processing item {content_id}: {str(e)}")
            self.db.update_status(content_id, 'failed', error_log=str(e))
            self.db.increment_retry(content_id)

if __name__ == "__main__":
    orch = PipelineOrchestrator()
    # 1. Populate data
    orch.run_trend_mining()
    # 2. Start loop
    orch.run_pipeline()
