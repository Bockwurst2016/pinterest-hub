import abc
from typing import List, Dict

class BaseTrendMiner(abc.ABC):
    """
    Abstract base class for trend mining modules.
    Every miner must implement the `fetch_trends` method.
    """
    
    @abc.abstractmethod
    def fetch_trends(self) -> List[Dict]:
        """
        Fetch trends from a specific source.
        Should return a list of dictionaries, each containing:
        - 'keyword': The identified trend keyword.
        - 'source': The source of the trend (e.g., 'Amazon', 'Pinterest').
        - 'confidence_score': A score from 0.0 to 1.0 based on trend strength.
        """
        pass

    @abc.abstractmethod
    def extract_products(self, keyword: str) -> List[Dict]:
        """
        Extract products associated with a specific keyword.
        Should return a list of dictionaries containing:
        - 'title': Product name.
        - 'description': Product summary.
        - 'amazon_link': URL to the product.
        """
        pass
