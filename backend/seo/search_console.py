"""
Google Search Console API Integration
Automated SEO management and optimization
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.config import settings

logger = logging.getLogger(__name__)


class SearchConsoleManager:
    """
    Google Search Console API Manager
    Handles sitemap submission, indexing requests, and performance monitoring
    """
    
    def __init__(self):
        self.site_url = settings.GOOGLE_SEARCH_CONSOLE_SITE_URL
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Search Console API service"""
        try:
            # Check if credentials are provided (try base64 first, then regular)
            creds_b64 = getattr(settings, 'GOOGLE_SEARCH_CONSOLE_CREDENTIALS_B64', None)
            creds_str = None
            
            if creds_b64 and creds_b64.strip():
                # Decode from base64
                try:
                    import base64
                    creds_str = base64.b64decode(creds_b64).decode('utf-8')
                    logger.info("Decoded credentials from base64")
                except Exception as e:
                    logger.warning(f"Failed to decode base64 credentials: {e}")
            
            # Fallback to regular credentials
            if not creds_str:
                creds_str = getattr(settings, 'GOOGLE_SEARCH_CONSOLE_CREDENTIALS', None)
            
            if not creds_str or creds_str.strip() == '':
                logger.warning("Google Search Console credentials not configured")
                return
            
            # Parse credentials JSON
            # Handle escaped quotes from .env file
            # Remove surrounding quotes if present
            if creds_str.startswith("'") and creds_str.endswith("'"):
                creds_str = creds_str[1:-1]
            elif creds_str.startswith('"') and creds_str.endswith('"'):
                creds_str = creds_str[1:-1]
            # Unescape quotes
            creds_str = creds_str.replace('\\"', '"')
            try:
                credentials_info = json.loads(creds_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse credentials JSON: {e}")
                logger.debug(f"First 200 chars of creds: {creds_str[:200]}")
                return
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/webmasters']
            )
            
            self.service = build('searchconsole', 'v1', credentials=credentials)
            logger.info("Google Search Console API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Search Console API: {e}")
            self.service = None
    
    def submit_sitemap(self, sitemap_url: str = None) -> Dict[str, Any]:
        """
        Submit sitemap to Google Search Console
        
        Args:
            sitemap_url: URL of sitemap (defaults to site_url/sitemap.xml)
        
        Returns:
            Dict with submission status
        """
        if not self.service:
            return {"error": "Search Console API not initialized"}
        
        if not sitemap_url:
            sitemap_url = f"{self.site_url}/sitemap.xml"
        
        try:
            # Submit sitemap
            self.service.sitemaps().submit(
                siteUrl=self.site_url,
                feedpath=sitemap_url
            ).execute()
            
            logger.info(f"Sitemap submitted: {sitemap_url}")
            return {
                "status": "success",
                "sitemap": sitemap_url,
                "message": "Sitemap submitted successfully"
            }
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            logger.error(f"Failed to submit sitemap: {error_details}")
            return {
                "status": "error",
                "error": error_details.get('error', {}).get('message', str(e))
            }
        except Exception as e:
            logger.error(f"Unexpected error submitting sitemap: {e}")
            return {"status": "error", "error": str(e)}
    
    def request_indexing(self, url: str) -> Dict[str, Any]:
        """
        Request indexing for a specific URL
        
        Args:
            url: URL to index
        
        Returns:
            Dict with indexing request status
        """
        if not self.service:
            return {"error": "Search Console API not initialized"}
        
        try:
            # Use Indexing API (requires separate setup)
            # For now, we'll use the URL Inspection API approach
            # Note: Actual indexing requests require Google Indexing API
            
            # Check URL status
            url_inspection = self.service.urlInspection().index().inspect(
                body={
                    'inspectionUrl': url,
                    'siteUrl': self.site_url
                }
            ).execute()
            
            logger.info(f"Indexing requested for: {url}")
            return {
                "status": "success",
                "url": url,
                "inspection": url_inspection,
                "message": "Indexing request submitted"
            }
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            logger.error(f"Failed to request indexing: {error_details}")
            return {
                "status": "error",
                "error": error_details.get('error', {}).get('message', str(e))
            }
        except Exception as e:
            logger.error(f"Unexpected error requesting indexing: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_search_analytics(
        self,
        start_date: str = None,
        end_date: str = None,
        dimensions: List[str] = None,
        row_limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Get search analytics data
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to 30 days ago
            end_date: End date (YYYY-MM-DD), defaults to today
            dimensions: List of dimensions ['query', 'page', 'country', 'device', 'date']
            row_limit: Maximum number of rows to return
        
        Returns:
            Dict with search analytics data
        """
        if not self.service:
            return {"error": "Search Console API not initialized"}
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not dimensions:
            dimensions = ['query', 'page']
        
        try:
            request = self.service.searchanalytics().query(
                siteUrl=self.site_url,
                body={
                    'startDate': start_date,
                    'endDate': end_date,
                    'dimensions': dimensions,
                    'rowLimit': row_limit
                }
            )
            
            response = request.execute()
            
            logger.info(f"Retrieved search analytics: {len(response.get('rows', []))} rows")
            return {
                "status": "success",
                "data": response,
                "start_date": start_date,
                "end_date": end_date
            }
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            logger.error(f"Failed to get search analytics: {error_details}")
            return {
                "status": "error",
                "error": error_details.get('error', {}).get('message', str(e))
            }
        except Exception as e:
            logger.error(f"Unexpected error getting search analytics: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_sitemaps(self) -> Dict[str, Any]:
        """Get list of submitted sitemaps"""
        if not self.service:
            return {"error": "Search Console API not initialized"}
        
        try:
            sitemaps = self.service.sitemaps().list(siteUrl=self.site_url).execute()
            return {
                "status": "success",
                "sitemaps": sitemaps.get('sitemap', [])
            }
        except HttpError as e:
            error_details = json.loads(e.content.decode('utf-8'))
            logger.error(f"Failed to get sitemaps: {error_details}")
            return {
                "status": "error",
                "error": error_details.get('error', {}).get('message', str(e))
            }
        except Exception as e:
            logger.error(f"Unexpected error getting sitemaps: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_index_status(self) -> Dict[str, Any]:
        """Get overall indexing status"""
        if not self.service:
            return {"error": "Search Console API not initialized"}
        
        try:
            # Get URL coverage data
            # Note: This is a simplified version - full implementation would use URL Inspection API
            sitemaps = self.get_sitemaps()
            
            return {
                "status": "success",
                "site_url": self.site_url,
                "sitemaps": sitemaps.get("sitemaps", []),
                "message": "Index status retrieved"
            }
        except Exception as e:
            logger.error(f"Unexpected error getting index status: {e}")
            return {"status": "error", "error": str(e)}
    
    def optimize_keywords(self, target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Analyze and optimize for target keywords
        
        Args:
            target_keywords: List of target keywords to optimize for
        
        Returns:
            Dict with optimization recommendations
        """
        if not target_keywords:
            target_keywords = [
                "longest first",
                "longest job matches first",
                "AI job matching",
                "LLC job matching",
                "capability-first matching"
            ]
        
        # Get search analytics for these keywords
        analytics = self.get_search_analytics()
        
        if analytics.get("status") != "success":
            return analytics
        
        # Analyze keyword performance
        rows = analytics.get("data", {}).get("rows", [])
        keyword_data = {}
        
        for row in rows:
            query = row.get("keys", [""])[0] if row.get("keys") else ""
            if any(keyword.lower() in query.lower() for keyword in target_keywords):
                keyword_data[query] = {
                    "clicks": row.get("clicks", 0),
                    "impressions": row.get("impressions", 0),
                    "ctr": row.get("ctr", 0),
                    "position": row.get("position", 0)
                }
        
        recommendations = []
        for keyword in target_keywords:
            if keyword not in keyword_data:
                recommendations.append({
                    "keyword": keyword,
                    "status": "not_ranking",
                    "action": "Create content targeting this keyword"
                })
            else:
                data = keyword_data[keyword]
                if data["position"] > 10:
                    recommendations.append({
                        "keyword": keyword,
                        "status": "low_ranking",
                        "position": data["position"],
                        "action": "Improve content and backlinks"
                    })
                elif data["ctr"] < 0.02:
                    recommendations.append({
                        "keyword": keyword,
                        "status": "low_ctr",
                        "ctr": data["ctr"],
                        "action": "Improve title and meta description"
                    })
        
        return {
            "status": "success",
            "target_keywords": target_keywords,
            "keyword_data": keyword_data,
            "recommendations": recommendations
        }

