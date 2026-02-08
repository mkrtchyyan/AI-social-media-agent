"""
Post Generator Module
Generates social media post captions and content based on brand profile
Uses OpenAI GPT-4 instead of Claude
"""

import openai
import json
import re


class PostGenerator:
    """
    Generates social media posts with multiple variations
    """
    
    def __init__(self, openai_api_key):
        """
        Initialize the post generator with OpenAI API
        
        Args:
            openai_api_key (str): API key for OpenAI
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    def generate_variations(self, brand_profile, intent, platform, constraints=None, 
                          rag_elements=None, num_variations=3):
        """
        Generate multiple variations of a social media post
        
        Args:
            brand_profile (dict): Brand profile from analyzer
            intent (str): What the post should accomplish
            platform (str): "linkedin" or "instagram"
            constraints (dict): Optional constraints (date, tone, CTA)
            rag_elements (dict): Optional elements (speaker names, images, etc.)
            num_variations (int): Number of variations to generate
            
        Returns:
            list: List of post variations
        """
        # Set platform-specific guidelines
        platform_specs = self._get_platform_specs(platform)
        
        # Build the generation prompt
        prompt = self._build_generation_prompt(
            brand_profile=brand_profile,
            intent=intent,
            platform=platform,
            platform_specs=platform_specs,
            constraints=constraints,
            rag_elements=rag_elements,
            num_variations=num_variations
        )
        
        try:
            print(f"🤖 Generating {num_variations} post variations...")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a social media content expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3000
            )
            
            # Extract response
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                variations = json.loads(json_match.group(1))
            else:
                variations = json.loads(response_text)
            
            # Add metadata to each variation
            for idx, variation in enumerate(variations['posts']):
                variation['platform'] = platform
                variation['intent'] = intent
                variation['variation_number'] = idx + 1
            
            return variations['posts']
            
        except Exception as e:
            print(f"❌ Error generating posts: {e}")
            return []
    
    def _build_generation_prompt(self, brand_profile, intent, platform, platform_specs, 
                                 constraints, rag_elements, num_variations):
        """
        Build the prompt for post generation
        
        Args:
            brand_profile (dict): Brand profile
            intent (str): Post intent
            platform (str): Social platform
            platform_specs (dict): Platform-specific specs
            constraints (dict): Optional constraints
            rag_elements (dict): Optional RAG elements
            num_variations (int): Number of variations
            
        Returns:
            str: Complete prompt
        """
        # Extract key brand characteristics
        tone = brand_profile['brand_voice']['tone']
        emoji_usage = brand_profile['brand_voice']['emoji_usage']
        cta_style = brand_profile['cta_style']['typical_ctas']
        
        # Build constraints section
        constraints_text = ""
        if constraints:
            constraints_text = f"\nADDITIONAL CONSTRAINTS:\n{json.dumps(constraints, indent=2)}"
        
        # Build RAG elements section
        rag_text = ""
        if rag_elements:
            rag_text = f"\nELEMENTS TO INCLUDE:\n{json.dumps(rag_elements, indent=2)}"
        
        prompt = f"""
You are a social media content creator. Generate {num_variations} variations of a {platform} post.

INTENT: {intent}

BRAND PROFILE:
- Tone: {tone}
- Emoji usage: {emoji_usage}
- Typical CTAs: {', '.join(cta_style[:3])}
- Brand voice: {json.dumps(brand_profile['brand_voice'], indent=2)}
- Messaging patterns: {json.dumps(brand_profile['messaging_patterns'], indent=2)}

PLATFORM SPECS ({platform.upper()}):
{json.dumps(platform_specs, indent=2)}
{constraints_text}
{rag_text}

Generate {num_variations} creative, on-brand variations. Each should be distinct in approach but aligned with brand voice.

Return in this JSON format:
{{
    "posts": [
        {{
            "caption": "Full post text here...",
            "overlay_text": "Short punchy text for image overlay (5-10 words max)",
            "hashtags": ["hashtag1", "hashtag2"],
            "cta": "Call to action",
            "hook": "Opening sentence or hook",
            "image_description": "Description of ideal background image",
            "reasoning": "Brief explanation of this variation's approach"
        }}
    ]
}}

Make the posts engaging, authentic, and truly aligned with the brand voice. Vary the approaches:
- Variation 1: More direct and action-oriented
- Variation 2: More storytelling or emotional
- Variation 3: More data-driven or informative

Return ONLY the JSON, no other text.
"""
        
        return prompt
    
    def _get_platform_specs(self, platform):
        """
        Get platform-specific specifications
        
        Args:
            platform (str): "linkedin" or "instagram"
            
        Returns:
            dict: Platform specifications
        """
        specs = {
            "linkedin": {
                "ideal_length": "150-300 words",
                "max_length": "3000 characters",
                "tone": "professional but conversational",
                "hashtags": "3-5 relevant hashtags",
                "line_breaks": "Use line breaks for readability",
                "emojis": "Use sparingly, professionally",
                "best_practices": [
                    "Start with a hook",
                    "Use short paragraphs",
                    "Include a clear CTA",
                    "Tag relevant people/companies when appropriate"
                ]
            },
            "instagram": {
                "ideal_length": "100-200 words",
                "max_length": "2200 characters",
                "tone": "casual and engaging",
                "hashtags": "5-10 relevant hashtags",
                "line_breaks": "Use line breaks and spacing",
                "emojis": "Use freely to enhance message",
                "best_practices": [
                    "Front-load the key message",
                    "Use emojis as visual breaks",
                    "Include relevant hashtags",
                    "Encourage engagement (likes, shares, comments)"
                ]
            }
        }
        
        return specs.get(platform, specs["linkedin"])
    
    def refine_with_feedback(self, post_data, user_feedback, brand_profile):
        """
        Refine a post based on user feedback
        
        Args:
            post_data (dict): Original post data
            user_feedback (str): User's feedback or requests
            brand_profile (dict): Brand profile
            
        Returns:
            dict: Refined post
        """
        prompt = f"""
You are refining a social media post based on user feedback.

ORIGINAL POST:
{json.dumps(post_data, indent=2)}

BRAND PROFILE:
{json.dumps(brand_profile, indent=2)}

USER FEEDBACK:
{user_feedback}

Generate an improved version that addresses the feedback while maintaining brand alignment.

Return in this JSON format:
{{
    "caption": "Updated post text...",
    "overlay_text": "Updated overlay text",
    "hashtags": ["hashtag1", "hashtag2"],
    "cta": "Updated CTA",
    "hook": "Updated hook",
    "image_description": "Updated image description",
    "changes_made": "Summary of what was changed and why"
}}

Return ONLY the JSON, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a social media expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                refined_post = json.loads(json_match.group(1))
            else:
                refined_post = json.loads(response_text)
            
            # Preserve original metadata
            refined_post['platform'] = post_data.get('platform')
            refined_post['intent'] = post_data.get('intent')
            
            return refined_post
            
        except Exception as e:
            print(f"❌ Error refining post: {e}")
            return post_data