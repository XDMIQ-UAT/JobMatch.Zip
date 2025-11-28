"""
Web Scraper Tool

Tool for scraping job descriptions and candidate profiles from URLs.
"""

from typing import Any, Dict, Optional
from src.tools.base_tool import BaseTool
import requests
from bs4 import BeautifulSoup


class WebScraperTool(BaseTool):
    """Tool for scraping content from web URLs."""
    
    name = "web_scraper"
    description = "Scrapes text content from web URLs (job descriptions, candidate profiles, etc.)"
    
    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        super().__init__()
        self.timeout = timeout
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    
    def execute(self, source: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            source: URL to scrape
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with 'content' (text) and 'metadata'
        """
        if not source.startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL: {source}")
        
        try:
            headers = {
                "User-Agent": self.user_agent
            }
            response = requests.get(source, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            metadata = {
                "url": source,
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": len(text)
            }
            
            return {
                "content": text,
                "metadata": metadata
            }
        
        except requests.RequestException as e:
            raise Exception(f"Failed to scrape URL {source}: {str(e)}")

