from src.miners.base_miner import BaseTrendMiner
from typing import List, Dict

class MockTrendMiner(BaseTrendMiner):
    """
    A mock miner for testing the pipeline logic without external API calls.
    """
    
    def fetch_trends(self) -> List[Dict]:
        print("[MockTrendMiner] Fetching mock trends...")
        return [
            {
                "keyword": "cozy minimalist living room",
                "source": "Pinterest Trends",
                "confidence_score": 0.95
            },
            {
                "keyword": "mechanical keyboard aesthetic",
                "source": "Amazon Bestsellers",
                "confidence_score": 0.88
            }
        ]

    def extract_products(self, keyword: str) -> List[Dict]:
        print(f"[MockTrendMiner] Extracting mock products for: {keyword}")
        
        if "cozy" in keyword:
            return [
                {
                    "title": "Soft Linen Throw Blanket",
                    "description": "A cozy, minimalist throw blanket in a neutral beige tone.",
                    "amazon_link": "https://amazon.com/mock-cozy-blanket"
                },
                {
                    "title": "Minimalist Oak Side Table",
                    "description": "Solid oak side table with a sleek, modern design.",
                    "amazon_link": "https://amazon.com/mock-oak-table"
                }
            ]
        else:
            return [
                {
                    "title": "Custom RGB Mechanical Keyboard",
                    "description": "A high-quality mechanical keyboard with customizable RGB lighting.",
                    "amazon_link": "https://amazon.com/mock-keyboard"
                }
            ]
