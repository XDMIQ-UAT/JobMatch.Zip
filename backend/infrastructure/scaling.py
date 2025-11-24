"""
Scaling utilities and infrastructure management.
Supports horizontal scaling, caching, and auto-scaling triggers.
"""
import logging
from typing import Optional
from redis import Redis
from elasticsearch import Elasticsearch

from backend.config import settings

logger = logging.getLogger(__name__)


class ScalingManager:
    """Manages scaling infrastructure components."""
    
    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.elasticsearch_client: Optional[Elasticsearch] = None
    
    def get_redis_client(self) -> Redis:
        """Get or create Redis client for caching."""
        if self.redis_client is None:
            self.redis_client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
        return self.redis_client
    
    def get_elasticsearch_client(self) -> Elasticsearch:
        """Get or create Elasticsearch client for search."""
        if self.elasticsearch_client is None:
            self.elasticsearch_client = Elasticsearch(
                [settings.ELASTICSEARCH_URL],
                request_timeout=30
            )
        return self.elasticsearch_client
    
    def check_redis_health(self) -> bool:
        """Check Redis connection health."""
        try:
            client = self.get_redis_client()
            return client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    def check_elasticsearch_health(self) -> bool:
        """Check Elasticsearch connection health."""
        try:
            client = self.get_elasticsearch_client()
            return client.ping()
        except Exception as e:
            logger.error(f"Elasticsearch health check failed: {e}")
            return False
    
    def get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix."""
        return f"{prefix}:{identifier}"
    
    def cache_get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            client = self.get_redis_client()
            return client.get(key)
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None
    
    def cache_set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            client = self.get_redis_client()
            client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False
    
    def cache_delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            client = self.get_redis_client()
            client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False


# Global scaling manager instance
scaling_manager = ScalingManager()


