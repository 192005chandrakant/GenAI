"""
Demo script for the Enhanced Misinformation Detection System
Shows how to use the new Gemini-powered misinformation detection features.
"""
import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, Any


class MisinformationDetectionDemo:
    """Demo class to showcase enhanced misinformation detection capabilities."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the demo with the API base URL."""
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/misinformation"
    
    def demo_analysis(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        """
        Demonstrate enhanced misinformation analysis.
        
        Args:
            content: Content to analyze
            content_type: Type of content (text, url, image, etc.)
            
        Returns:
            Analysis result from the API
        """
        print(f"\n🔍 Analyzing content: {content[:100]}...")
        
        payload = {
            "content": content,
            "content_type": content_type,
            "user_language": "auto",
            "context": {
                "demo": True,
                "source": "demo_script",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.post(f"{self.api_url}/analyze", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self._display_analysis_result(result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return {}
    
    def demo_batch_analysis(self, contents: list) -> Dict[str, Any]:
        """
        Demonstrate batch analysis of multiple content items.
        
        Args:
            contents: List of content items to analyze
            
        Returns:
            Batch analysis result from the API
        """
        print(f"\n📦 Starting batch analysis of {len(contents)} items...")
        
        payload = {
            "contents": contents,
            "content_types": ["text"] * len(contents),
            "priority": "normal",
            "user_id": "demo_user"
        }
        
        try:
            response = requests.post(f"{self.api_url}/analyze/batch", json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            self._display_batch_result(result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Batch analysis failed: {e}")
            return {}
    
    def demo_claim_extraction(self, content: str) -> Dict[str, Any]:
        """
        Demonstrate claim extraction without full analysis.
        
        Args:
            content: Content to extract claims from
            
        Returns:
            Claim extraction result
        """
        print(f"\n📋 Extracting claims from: {content[:100]}...")
        
        params = {
            "content": content,
            "language": "auto"
        }
        
        try:
            response = requests.get(f"{self.api_url}/claims/extract", params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self._display_claims_result(result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Claim extraction failed: {e}")
            return {}
    
    def demo_evidence_search(self, claims: list) -> Dict[str, Any]:
        """
        Demonstrate evidence search for specific claims.
        
        Args:
            claims: List of claims to search evidence for
            
        Returns:
            Evidence search result
        """
        print(f"\n🔍 Searching evidence for {len(claims)} claims...")
        
        params = {
            "claims": claims,
            "language": "en",
            "max_results": 5
        }
        
        try:
            response = requests.get(f"{self.api_url}/evidence/search", params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self._display_evidence_result(result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Evidence search failed: {e}")
            return {}
    
    def _display_analysis_result(self, result: Dict[str, Any]):
        """Display the analysis result in a formatted way."""
        print("\n" + "="*60)
        print("🎯 MISINFORMATION ANALYSIS RESULT")
        print("="*60)
        
        # Basic metrics
        print(f"📊 Credibility Score: {result.get('score', 'N/A')}/100")
        print(f"🚦 Badge: {result.get('badge', 'N/A').upper()}")
        print(f"⚖️  Verdict: {result.get('verdict', 'N/A')}")
        print(f"🌐 Language: {result.get('language', 'N/A')}")
        print(f"🤖 Model: {result.get('processing_model', 'N/A')}")
        print(f"⚡ Processing Time: {result.get('processing_time', 'N/A')}s")
        
        # Claims
        claims = result.get('claims', [])
        if claims:
            print(f"\n📋 EXTRACTED CLAIMS ({len(claims)}):")
            for i, claim in enumerate(claims, 1):
                print(f"  {i}. {claim.get('claim_text', 'N/A')}")
                if claim.get('who'):
                    print(f"     👤 Who: {claim['who']}")
                if claim.get('where'):
                    print(f"     📍 Where: {claim['where']}")
                if claim.get('when'):
                    print(f"     📅 When: {claim['when']}")
                print(f"     🎯 Confidence: {claim.get('confidence', 0):.2f}")
        
        # Citations
        citations = result.get('citations', [])
        if citations:
            print(f"\n📚 EVIDENCE CITATIONS ({len(citations)}):")
            for i, citation in enumerate(citations, 1):
                print(f"  {i}. {citation.get('title', 'N/A')}")
                print(f"     🔗 {citation.get('url', 'N/A')}")
                print(f"     📝 {citation.get('snippet', 'N/A')[:100]}...")
                print(f"     📊 Relevance: {citation.get('relevance_score', 0):.2f}")
                print(f"     🏷️  Type: {citation.get('source_type', 'N/A')}")
        
        # Manipulation techniques
        techniques = result.get('manipulation_techniques', [])
        if techniques:
            print(f"\n⚠️  MANIPULATION TECHNIQUES ({len(techniques)}):")
            for technique in techniques:
                print(f"  • {technique.replace('_', ' ').title()}")
        
        # Learn card
        learn_card = result.get('learn_card', {})
        if learn_card:
            print(f"\n📚 EDUCATIONAL CONTENT:")
            print(f"  💡 {learn_card.get('title', 'N/A')}")
            print(f"     {learn_card.get('content', 'N/A')}")
            print(f"  💭 Tip: {learn_card.get('tip', 'N/A')}")
            print(f"  🏷️  Category: {learn_card.get('category', 'N/A')}")
        
        # Analysis explanation
        explanation = result.get('explanation', '')
        if explanation:
            print(f"\n🔍 DETAILED EXPLANATION:")
            print(f"  {explanation}")
        
        print("="*60)
    
    def _display_batch_result(self, result: Dict[str, Any]):
        """Display batch analysis result."""
        print("\n" + "="*60)
        print("📦 BATCH ANALYSIS RESULT")
        print("="*60)
        
        print(f"🆔 Batch ID: {result.get('batch_id', 'N/A')}")
        print(f"📊 Total Items: {result.get('total_items', 0)}")
        print(f"✅ Completed: {result.get('completed_items', 0)}")
        print(f"❌ Failed: {result.get('failed_items', 0)}")
        print(f"🔄 Status: {result.get('status', 'N/A').upper()}")
        
        results = result.get('results', [])
        if results:
            print(f"\n📋 INDIVIDUAL RESULTS:")
            for i, item_result in enumerate(results, 1):
                score = item_result.get('score', 'N/A')
                badge = item_result.get('badge', 'N/A').upper()
                verdict = item_result.get('verdict', 'N/A')
                print(f"  {i}. Score: {score}/100 | Badge: {badge} | {verdict[:50]}...")
        
        print("="*60)
    
    def _display_claims_result(self, result: Dict[str, Any]):
        """Display claim extraction result."""
        print("\n" + "="*40)
        print("📋 CLAIM EXTRACTION RESULT")
        print("="*40)
        
        print(f"🌐 Detected Language: {result.get('detected_language', 'N/A')}")
        print(f"📊 Total Claims: {result.get('total_claims', 0)}")
        
        claims = result.get('claims', [])
        if claims:
            print(f"\n📝 EXTRACTED CLAIMS:")
            for i, claim in enumerate(claims, 1):
                print(f"  {i}. {claim.get('claim_text', 'N/A')}")
                print(f"     🎯 Confidence: {claim.get('confidence', 0):.2f}")
        
        print("="*40)
    
    def _display_evidence_result(self, result: Dict[str, Any]):
        """Display evidence search result."""
        print("\n" + "="*50)
        print("🔍 EVIDENCE SEARCH RESULT")
        print("="*50)
        
        print(f"🔍 Query: {result.get('query', 'N/A')}")
        print(f"📊 Total Results: {result.get('total_results', 0)}")
        print(f"⏱️  Search Time: {result.get('search_time', 0):.2f}s")
        
        sources = result.get('sources_searched', [])
        if sources:
            print(f"🏪 Sources Searched: {', '.join(sources)}")
        
        citations = result.get('citations', [])
        if citations:
            print(f"\n📚 FOUND CITATIONS ({len(citations)}):")
            for i, citation in enumerate(citations, 1):
                print(f"  {i}. {citation.get('title', 'N/A')}")
                print(f"     🔗 {citation.get('url', 'N/A')}")
                print(f"     📊 Relevance: {citation.get('relevance_score', 0):.2f}")
        
        print("="*50)


def main():
    """Run the demonstration."""
    print("🚀 Enhanced Misinformation Detection System Demo")
    print("=" * 60)
    
    demo = MisinformationDetectionDemo()
    
    # Demo 1: Single content analysis
    print("\n1️⃣ SINGLE CONTENT ANALYSIS DEMO")
    demo.demo_analysis(
        "Drinking hot water every 15 minutes kills coronavirus and prevents all diseases.",
        "text"
    )
    
    # Demo 2: Claim extraction only
    print("\n2️⃣ CLAIM EXTRACTION DEMO")
    demo.demo_claim_extraction(
        "5G towers cause cancer and vaccines contain microchips for government tracking."
    )
    
    # Demo 3: Evidence search
    print("\n3️⃣ EVIDENCE SEARCH DEMO")
    demo.demo_evidence_search([
        "Vaccines contain microchips",
        "5G towers cause cancer"
    ])
    
    # Demo 4: Batch analysis
    print("\n4️⃣ BATCH ANALYSIS DEMO")
    demo.demo_batch_analysis([
        "The Earth is flat and NASA is hiding the truth.",
        "Climate change is a hoax created by scientists.",
        "COVID-19 vaccines alter your DNA permanently."
    ])
    
    # Demo 5: Different content types
    print("\n5️⃣ VARIED CONTENT ANALYSIS")
    
    # Credible content
    demo.demo_analysis(
        "According to the World Health Organization, vaccines are safe and effective at preventing diseases.",
        "text"
    )
    
    # Mixed content needing context
    demo.demo_analysis(
        "Studies show that vitamin D deficiency is linked to severe COVID-19 outcomes.",
        "text"
    )
    
    print("\n✅ Demo completed! Check the API documentation for more details.")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔗 Enhanced endpoints: /api/v1/misinformation/")


if __name__ == "__main__":
    main()