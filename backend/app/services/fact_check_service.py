"""
Fact Check Service for Google Fact Check Tools API and RSS feeds integration.
Provides real-time fact-checking capabilities and source verification.
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse

import aiohttp
import feedparser
from bs4 import BeautifulSoup

from app.core.config import settings
from app.models.schemas import Citation, SourceCategory, VerdictType

logger = logging.getLogger(__name__)


class FactCheckService:
    """Service for fact-checking and source verification."""
    
    def __init__(self):
        """Initialize Fact Check service."""
        self.api_key = settings.FACT_CHECK_API_KEY
        self.api_url = getattr(settings, 'FACT_CHECK_API_URL', 'https://factchecktools.googleapis.com/v1alpha1/claims:search')
        self.rss_feeds = getattr(settings, 'RSS_FEEDS', [])
        self.session = None
        
        logger.info("Fact Check Service initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_fact_checks(
        self, 
        query: str, 
        language: str = "en",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for fact checks using Google Fact Check Tools API.
        
        Args:
            query: Search query
            language: Language code
            max_results: Maximum number of results
            
        Returns:
            List of fact check results
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            params = {
                "key": self.api_key,
                "query": query,
                "languageCode": language,
                "maxAgeDays": 365,  # Last year
                "pageSize": min(max_results, 20)
            }
            
            async with self.session.get(self.api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_fact_check_results(data)
                else:
                    logger.error(f"Fact Check API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching fact checks: {str(e)}")
            return []
    
    async def get_rss_fact_checks(
        self, 
        query: str = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get fact checks from RSS feeds.
        
        Args:
            query: Optional search query to filter results
            max_results: Maximum number of results
            
        Returns:
            List of fact check results from RSS feeds
        """
        try:
            all_entries = []
            
            for feed_url in self.rss_feeds:
                try:
                    entries = await self._fetch_rss_feed(feed_url, query)
                    all_entries.extend(entries)
                except Exception as e:
                    logger.error(f"Error fetching RSS feed {feed_url}: {str(e)}")
                    continue
            
            # Sort by date and limit results
            all_entries.sort(key=lambda x: x.get("published_date", datetime.min), reverse=True)
            return all_entries[:max_results]
            
        except Exception as e:
            logger.error(f"Error getting RSS fact checks: {str(e)}")
            return []
    
    async def verify_claim(
        self, 
        claim: str, 
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Verify a claim using multiple sources.
        
        Args:
            claim: Claim to verify
            language: Language code
            
        Returns:
            Verification results
        """
        try:
            start_time = time.time()
            
            # Search fact check API
            fact_check_results = await self.search_fact_checks(claim, language)
            
            # Search RSS feeds
            rss_results = await self.get_rss_fact_checks(claim)
            
            # Combine and analyze results
            combined_results = self._combine_verification_results(
                fact_check_results, rss_results, claim
            )
            
            # Calculate overall verdict
            verdict = self._calculate_overall_verdict(combined_results)
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return {
                "claim": claim,
                "verdict": verdict,
                "sources": combined_results,
                "total_sources": len(combined_results),
                "latency_ms": latency_ms,
                "confidence": self._calculate_confidence(combined_results)
            }
            
        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            return {
                "claim": claim,
                "verdict": VerdictType.UNVERIFIED.value,
                "sources": [],
                "total_sources": 0,
                "latency_ms": 0,
                "confidence": 0.0
            }
    
    async def get_source_credibility(self, domain: str) -> Dict[str, Any]:
        """
        Get credibility information for a domain.
        
        Args:
            domain: Domain to check
            
        Returns:
            Credibility information
        """
        try:
            # This would integrate with a domain credibility database
            # For now, return basic information
            return {
                "domain": domain,
                "credibility_score": self._get_default_credibility_score(domain),
                "category": self._categorize_domain(domain),
                "last_verified": datetime.utcnow(),
                "verification_count": 1
            }
            
        except Exception as e:
            logger.error(f"Error getting source credibility: {str(e)}")
            return {
                "domain": domain,
                "credibility_score": 50.0,
                "category": SourceCategory.NEWS.value,
                "last_verified": datetime.utcnow(),
                "verification_count": 0
            }
    
    async def batch_verify_claims(
        self, 
        claims: List[str], 
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        Verify multiple claims in batch.
        
        Args:
            claims: List of claims to verify
            language: Language code
            
        Returns:
            List of verification results
        """
        try:
            tasks = [
                self.verify_claim(claim, language) 
                for claim in claims
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Batch verification error: {str(result)}")
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch verification: {str(e)}")
            return []
    
    # Private helper methods
    
    async def _fetch_rss_feed(self, feed_url: str, query: str = None) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse RSS feed
                    feed = feedparser.parse(content)
                    
                    entries = []
                    for entry in feed.entries:
                        # Filter by query if provided
                        if query and query.lower() not in entry.title.lower():
                            continue
                        
                        entry_data = {
                            "title": entry.title,
                            "url": entry.link,
                            "description": entry.get("description", ""),
                            "published_date": self._parse_date(entry.get("published", "")),
                            "source": feed.feed.get("title", ""),
                            "domain": urlparse(entry.link).netloc,
                            "category": self._categorize_rss_source(feed_url)
                        }
                        
                        entries.append(entry_data)
                    
                    return entries
                else:
                    logger.error(f"RSS feed error {feed_url}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {str(e)}")
            return []
    
    def _parse_fact_check_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse fact check API results."""
        try:
            results = []
            
            for claim in data.get("claims", []):
                claim_data = {
                    "title": claim.get("text", ""),
                    "url": claim.get("claimReview", [{}])[0].get("url", ""),
                    "description": claim.get("claimReview", [{}])[0].get("title", ""),
                    "published_date": self._parse_date(claim.get("claimDate", "")),
                    "source": claim.get("claimReview", [{}])[0].get("publisher", {}).get("name", ""),
                    "domain": urlparse(claim.get("claimReview", [{}])[0].get("url", "")).netloc,
                    "category": SourceCategory.FACT_CHECK.value,
                    "verdict": claim.get("claimReview", [{}])[0].get("textualRating", ""),
                    "language": claim.get("claimReview", [{}])[0].get("languageCode", "en")
                }
                
                results.append(claim_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing fact check results: {str(e)}")
            return []
    
    def _combine_verification_results(
        self, 
        fact_check_results: List[Dict[str, Any]], 
        rss_results: List[Dict[str, Any]],
        original_claim: str
    ) -> List[Dict[str, Any]]:
        """Combine results from different sources."""
        combined = []
        
        # Add fact check results
        for result in fact_check_results:
            combined.append({
                **result,
                "source_type": "fact_check_api",
                "relevance_score": self._calculate_relevance(result, original_claim)
            })
        
        # Add RSS results
        for result in rss_results:
            combined.append({
                **result,
                "source_type": "rss_feed",
                "relevance_score": self._calculate_relevance(result, original_claim)
            })
        
        # Sort by relevance and date
        combined.sort(key=lambda x: (x.get("relevance_score", 0), x.get("published_date", datetime.min)), reverse=True)
        
        return combined
    
    def _calculate_relevance(self, result: Dict[str, Any], original_claim: str) -> float:
        """Calculate relevance score between result and original claim."""
        try:
            title = result.get("title", "").lower()
            description = result.get("description", "").lower()
            claim_words = set(original_claim.lower().split())
            
            # Simple word overlap calculation
            title_words = set(title.split())
            desc_words = set(description.split())
            
            title_overlap = len(claim_words.intersection(title_words)) / len(claim_words) if claim_words else 0
            desc_overlap = len(claim_words.intersection(desc_words)) / len(claim_words) if claim_words else 0
            
            return (title_overlap * 0.7) + (desc_overlap * 0.3)
            
        except Exception:
            return 0.0
    
    def _calculate_overall_verdict(self, results: List[Dict[str, Any]]) -> str:
        """Calculate overall verdict from multiple sources."""
        if not results:
            return VerdictType.UNVERIFIED.value
        
        # Count verdicts
        verdict_counts = {}
        for result in results:
            verdict = result.get("verdict", "").lower()
            if verdict:
                verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        if not verdict_counts:
            return VerdictType.UNVERIFIED.value
        
        # Return most common verdict
        return max(verdict_counts.items(), key=lambda x: x[1])[0]
    
    def _calculate_confidence(self, results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on number and quality of sources."""
        if not results:
            return 0.0
        
        # Base confidence on number of sources
        base_confidence = min(len(results) / 5.0, 1.0)
        
        # Adjust for source quality
        quality_scores = []
        for result in results:
            domain = result.get("domain", "")
            credibility = self._get_default_credibility_score(domain)
            quality_scores.append(credibility / 100.0)
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            return (base_confidence * 0.6) + (avg_quality * 0.4)
        
        return base_confidence
    
    def _get_default_credibility_score(self, domain: str) -> float:
        """Get default credibility score for a domain."""
        # This would be replaced with a proper domain credibility database
        trusted_domains = {
            "reuters.com": 95.0,
            "bbc.com": 95.0,
            "ap.org": 95.0,
            "factcheck.org": 90.0,
            "snopes.com": 90.0,
            "politifact.com": 90.0,
            "washingtonpost.com": 85.0,
            "nytimes.com": 85.0,
            "theguardian.com": 85.0
        }
        
        return trusted_domains.get(domain.lower(), 50.0)
    
    def _categorize_domain(self, domain: str) -> str:
        """Categorize domain by type."""
        domain_lower = domain.lower()
        
        if any(keyword in domain_lower for keyword in ["factcheck", "snopes", "politifact"]):
            return SourceCategory.FACT_CHECK.value
        elif any(keyword in domain_lower for keyword in ["edu", "academic"]):
            return SourceCategory.ACADEMIC.value
        elif any(keyword in domain_lower for keyword in ["gov", "government"]):
            return SourceCategory.GOVERNMENT.value
        else:
            return SourceCategory.NEWS.value
    
    def _categorize_rss_source(self, feed_url: str) -> str:
        """Categorize RSS source by URL."""
        if "factcheck" in feed_url:
            return SourceCategory.FACT_CHECK.value
        elif "reuters" in feed_url or "bbc" in feed_url:
            return SourceCategory.NEWS.value
        else:
            return SourceCategory.NEWS.value
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            # Try common date formats
            formats = [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, return current time
            return datetime.utcnow()
            
        except Exception:
            return datetime.utcnow()


# Create a singleton instance
fact_check_service = FactCheckService()
