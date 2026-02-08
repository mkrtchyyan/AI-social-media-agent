"""
Brand Analyzer Module
Analyzes company brand materials to extract voice, tone, colors, and messaging patterns
Uses OpenAI GPT-4 instead of Claude
"""

import openai
import requests
from bs4 import BeautifulSoup
import json
import re


class BrandAnalyzer:
    """
    Analyzes brand materials to create a comprehensive brand profile
    """
    
    def __init__(self, openai_api_key):
        """
        Initialize the brand analyzer with OpenAI API
        
        Args:
            openai_api_key (str): API key for OpenAI
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        
    def scrape_website(self, url):
        """
        Scrape website content for brand analysis
        
        Args:
            url (str): Website URL to scrape
            
        Returns:
            str: Extracted text content from website
        """
        try:
            print(f"🌐 Scraping website: {url}")
            
            # Set a user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Limit to first 5000 characters to avoid token limits
            return text[:5000]
            
        except Exception as e:
            print(f"⚠️ Warning: Could not scrape website: {e}")
            return ""
    
    def analyze(self, website_url=None, existing_posts=None, brand_guidelines=None):
        """
        Main analysis method to create brand profile
        
        Args:
            website_url (str): Company website URL
            existing_posts (list): List of existing social media posts
            brand_guidelines (dict): Optional brand guidelines
            
        Returns:
            dict: Comprehensive brand profile
        """
        # Gather all brand materials
        website_content = ""
        if website_url:
            website_content = self.scrape_website(website_url)
        
        posts_text = ""
        if existing_posts:
            posts_text = "\n\n".join(existing_posts)
        
        guidelines_text = ""
        if brand_guidelines:
            guidelines_text = json.dumps(brand_guidelines, indent=2)
        
        # Create analysis prompt for GPT-4
        analysis_prompt = f"""
You are a brand strategist analyzing company materials to extract brand characteristics.

Analyze the following materials and create a comprehensive brand profile:

WEBSITE CONTENT:
{website_content if website_content else "Not provided"}

EXISTING SOCIAL MEDIA POSTS:
{posts_text if posts_text else "Not provided"}

BRAND GUIDELINES:
{guidelines_text if guidelines_text else "Not provided"}

Extract and return the following in JSON format:

{{
    "brand_voice": {{
        "tone": "formal/casual/playful/professional/inspirational",
        "personality_traits": ["trait1", "trait2", "trait3"],
        "emoji_usage": "none/minimal/moderate/frequent",
        "sentence_style": "short and punchy/medium/long and detailed",
        "language_complexity": "simple/moderate/sophisticated"
    }},
    "visual_identity": {{
        "primary_colors": ["#hexcolor1", "#hexcolor2"],
        "design_style": "minimal/bold/corporate/creative/tech-focused",
        "imagery_style": "abstract/photographic/illustrated/mixed"
    }},
    "messaging_patterns": {{
        "key_themes": ["theme1", "theme2", "theme3"],
        "value_propositions": ["value1", "value2"],
        "target_audience": "description of target audience",
        "common_topics": ["topic1", "topic2", "topic3"]
    }},
    "cta_style": {{
        "typical_ctas": ["CTA1", "CTA2", "CTA3"],
        "cta_placement": "beginning/middle/end",
        "cta_tone": "urgent/casual/professional/friendly"
    }},
    "content_structure": {{
        "typical_post_length": "short/medium/long",
        "uses_hashtags": true/false,
        "hashtag_count": "number or range",
        "uses_questions": true/false,
        "uses_statistics": true/false
    }}
}}

Be specific and evidence-based. If information is not available, make reasonable inferences based on industry standards.
Return ONLY the JSON, no other text.
"""
        
        try:
            print("🤖 Analyzing brand with GPT-4...")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # or "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": "You are a brand analysis expert. Always respond with valid JSON only."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract the response
            response_text = response.choices[0].message.content
            
            # Parse JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                brand_profile = json.loads(json_match.group(1))
            else:
                # Try to parse directly
                brand_profile = json.loads(response_text)
            
            print("✅ Brand analysis complete!")
            return brand_profile
            
        except Exception as e:
            print(f"❌ Error during brand analysis: {e}")
            # Return a default brand profile if analysis fails
            return self._default_brand_profile()
    
    def _default_brand_profile(self):
        """
        Return a default brand profile as fallback
        
        Returns:
            dict: Default brand profile
        """
        return {
            "brand_voice": {
                "tone": "professional",
                "personality_traits": ["innovative", "reliable", "forward-thinking"],
                "emoji_usage": "moderate",
                "sentence_style": "medium",
                "language_complexity": "moderate"
            },
            "visual_identity": {
                "primary_colors": ["#1a73e8", "#34a853"],
                "design_style": "modern",
                "imagery_style": "photographic"
            },
            "messaging_patterns": {
                "key_themes": ["innovation", "technology", "growth"],
                "value_propositions": ["cutting-edge solutions", "reliable service"],
                "target_audience": "tech-savvy professionals",
                "common_topics": ["AI", "technology", "business"]
            },
            "cta_style": {
                "typical_ctas": ["Learn more", "Get started", "Join us"],
                "cta_placement": "end",
                "cta_tone": "professional"
            },
            "content_structure": {
                "typical_post_length": "medium",
                "uses_hashtags": True,
                "hashtag_count": "3-5",
                "uses_questions": True,
                "uses_statistics": False
            }
        }