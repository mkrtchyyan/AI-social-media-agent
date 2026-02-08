"""
Feedback Loop Module
Implements agentic self-feedback where AI critiques and improves its own outputs
Uses OpenAI GPT-4 instead of Claude
"""

import openai
import json
import re


class FeedbackLoop:
    """
    Runs iterative self-improvement on generated posts
    """
    
    def __init__(self, openai_api_key):
        """
        Initialize the feedback loop with OpenAI API
        
        Args:
            openai_api_key (str): API key for OpenAI
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    def iterate(self, post, brand_profile, platform, iterations=2):
        """
        Run multiple iterations of self-critique and improvement
        
        Args:
            post (dict): Initial post data
            brand_profile (dict): Brand profile
            platform (str): Social platform
            iterations (int): Number of improvement iterations
            
        Returns:
            dict: Improved post after iterations
        """
        current_post = post.copy()
        
        for i in range(iterations):
            print(f"  🔄 Iteration {i + 1}/{iterations}")
            
            # Step 1: Critique the current post
            critique = self._critique_post(current_post, brand_profile, platform)
            
            # Step 2: Improve based on critique
            current_post = self._improve_post(current_post, critique, brand_profile, platform)
        
        return current_post
    
    def _critique_post(self, post, brand_profile, platform):
        """
        AI critiques the post against quality criteria
        
        Args:
            post (dict): Post to critique
            brand_profile (dict): Brand profile
            platform (str): Social platform
            
        Returns:
            dict: Critique with scores and suggestions
        """
        critique_prompt = f"""
You are a critical brand manager reviewing a social media post. Be constructive but thorough.

POST TO REVIEW:
Caption: {post.get('caption', '')}
Overlay Text: {post.get('overlay_text', '')}
Image Description: {post.get('image_description', '')}
Platform: {platform}

BRAND GUIDELINES:
{json.dumps(brand_profile, indent=2)}

Evaluate the post on these criteria (rate 1-10 for each):

1. BRAND CONSISTENCY
   - Does it match the brand voice and tone?
   - Is the language style consistent?
   - Does it reflect brand values?

2. MESSAGE CLARITY
   - Is the main message clear and focused?
   - Is it easy to understand quickly?
   - Does it avoid jargon or confusion?

3. CTA EFFECTIVENESS
   - Is there a clear call-to-action?
   - Is the CTA compelling and specific?
   - Is it positioned well?

4. TEXT READABILITY ON IMAGE
   - Is the overlay text short enough?
   - Will it be readable on mobile?
   - Does it complement the caption?

5. PLATFORM APPROPRIATENESS
   - Does it fit {platform} best practices?
   - Is the length appropriate?
   - Does it use platform features well (hashtags, etc.)?

6. ENGAGEMENT POTENTIAL
   - Will this capture attention?
   - Does it encourage interaction?
   - Is it shareable?

Return in JSON format:
{{
    "scores": {{
        "brand_consistency": 8,
        "message_clarity": 7,
        "cta_effectiveness": 6,
        "text_readability": 9,
        "platform_appropriateness": 8,
        "engagement_potential": 7
    }},
    "overall_score": 7.5,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "specific_improvements": [
        "Specific suggestion 1",
        "Specific suggestion 2",
        "Specific suggestion 3"
    ],
    "priority_fix": "The single most important thing to improve"
}}

Be specific and actionable in your feedback.
Return ONLY the JSON, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a brand review expert. Always respond with valid JSON only."},
                    {"role": "user", "content": critique_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                critique = json.loads(json_match.group(1))
            else:
                critique = json.loads(response_text)
            
            return critique
            
        except Exception as e:
            print(f"⚠️ Critique error: {e}")
            return self._default_critique()
    
    def _improve_post(self, post, critique, brand_profile, platform):
        """
        Improve the post based on critique
        
        Args:
            post (dict): Current post
            critique (dict): Critique results
            brand_profile (dict): Brand profile
            platform (str): Social platform
            
        Returns:
            dict: Improved post
        """
        improvement_prompt = f"""
You are improving a social media post based on expert feedback.

CURRENT POST:
{json.dumps(post, indent=2)}

CRITIQUE RECEIVED:
Overall Score: {critique.get('overall_score', 7)}/10
Weaknesses: {', '.join(critique.get('weaknesses', []))}
Priority Fix: {critique.get('priority_fix', 'Improve overall quality')}
Specific Improvements Needed:
{chr(10).join([f"- {imp}" for imp in critique.get('specific_improvements', [])])}

BRAND PROFILE:
{json.dumps(brand_profile, indent=2)}

Create an improved version that addresses the critique while maintaining what worked well.
Focus especially on the priority fix and specific improvements.

Return in JSON format:
{{
    "caption": "Improved caption...",
    "overlay_text": "Improved overlay text",
    "hashtags": ["hashtag1", "hashtag2"],
    "cta": "Improved CTA",
    "hook": "Improved hook",
    "image_description": "Improved image description",
    "improvements_made": "Brief summary of what was improved"
}}

Return ONLY the JSON, no other text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a social media improvement expert. Always respond with valid JSON only."},
                    {"role": "user", "content": improvement_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                improved_post = json.loads(json_match.group(1))
            else:
                improved_post = json.loads(response_text)
            
            # Preserve metadata
            improved_post['platform'] = post.get('platform')
            improved_post['intent'] = post.get('intent')
            improved_post['variation_number'] = post.get('variation_number')
            improved_post['critique_score'] = critique.get('overall_score')
            
            return improved_post
            
        except Exception as e:
            print(f"⚠️ Improvement error: {e}")
            return post
    
    def _default_critique(self):
        """
        Return a default critique if API call fails
        
        Returns:
            dict: Default critique
        """
        return {
            "scores": {
                "brand_consistency": 7,
                "message_clarity": 7,
                "cta_effectiveness": 7,
                "text_readability": 7,
                "platform_appropriateness": 7,
                "engagement_potential": 7
            },
            "overall_score": 7.0,
            "strengths": ["Clear message"],
            "weaknesses": ["Could be more engaging"],
            "specific_improvements": ["Enhance the hook", "Strengthen the CTA"],
            "priority_fix": "Make the opening more attention-grabbing"
        }