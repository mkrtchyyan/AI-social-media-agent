"""
Main application file for AI Social Media Agent
This orchestrates all the components and handles the main workflow
"""

import os
from dotenv import load_dotenv
from brand_analyzer import BrandAnalyzer
from post_generator import PostGenerator
from feedback_loop import FeedbackLoop
from image_generator import ImageGenerator
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class SocialMediaAgent:
    """
    Main class that coordinates all components of the social media agent
    """
    
    def __init__(self):
        """Initialize all components with API keys from environment"""
        # Get API key from environment variables
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize all modules (all now use OpenAI)
        self.brand_analyzer = BrandAnalyzer(self.openai_api_key)
        self.post_generator = PostGenerator(self.openai_api_key)
        self.feedback_loop = FeedbackLoop(self.openai_api_key)
        self.image_generator = ImageGenerator(self.openai_api_key)
        
        # Store brand profile after analysis
        self.brand_profile = None
        
    def analyze_brand(self, website_url=None, existing_posts=None, brand_guidelines=None):
        """
        Analyze brand materials to extract brand voice and visual identity
        
        Args:
            website_url (str): URL of company website
            existing_posts (list): List of existing social media posts
            brand_guidelines (dict): Optional brand guidelines
            
        Returns:
            dict: Brand profile with voice, colors, tone, etc.
        """
        print("🔍 Analyzing brand identity...")
        
        # Use the brand analyzer to extract brand characteristics
        self.brand_profile = self.brand_analyzer.analyze(
            website_url=website_url,
            existing_posts=existing_posts,
            brand_guidelines=brand_guidelines
        )
        
        print("✅ Brand analysis complete!")
        return self.brand_profile
    
    def generate_post(self, intent, platform="linkedin", constraints=None, rag_elements=None):
        """
        Generate a social media post with multiple variations
        
        Args:
            intent (str): What the post is about (e.g., "Announce hackathon")
            platform (str): "linkedin" or "instagram"
            constraints (dict): Optional constraints (date, tone, CTA)
            rag_elements (dict): Optional elements like speaker names, images
            
        Returns:
            dict: Post variations with captions and images
        """
        if not self.brand_profile:
            raise ValueError("Brand profile not set. Run analyze_brand() first!")
        
        print(f"📝 Generating {platform} post for: {intent}")
        
        # Step 1: Generate initial post variations (3 versions)
        initial_posts = self.post_generator.generate_variations(
            brand_profile=self.brand_profile,
            intent=intent,
            platform=platform,
            constraints=constraints,
            rag_elements=rag_elements,
            num_variations=3
        )
        
        # Step 2: Run feedback loop on each variation
        improved_posts = []
        for idx, post in enumerate(initial_posts):
            print(f"🔄 Running feedback loop on variation {idx + 1}...")
            
            # AI critiques and improves the post 2-3 times
            improved_post = self.feedback_loop.iterate(
                post=post,
                brand_profile=self.brand_profile,
                platform=platform,
                iterations=2
            )
            improved_posts.append(improved_post)
        
        # Step 3: Generate images for each improved post
        final_posts = []
        for idx, post in enumerate(improved_posts):
            print(f"🎨 Generating image for variation {idx + 1}...")
            
            # Generate background image
            image_path = self.image_generator.generate_background(
                post_data=post,
                brand_profile=self.brand_profile,
                platform=platform
            )
            
            # Add text overlay to image
            final_image_path = self.image_generator.add_text_overlay(
                image_path=image_path,
                text=post.get('overlay_text', ''),
                brand_profile=self.brand_profile
            )
            
            post['image_path'] = final_image_path
            final_posts.append(post)
        
        print("✅ Post generation complete!")
        return final_posts
    
    def refine_post(self, post_data, user_feedback):
        """
        Refine a selected post based on user feedback
        
        Args:
            post_data (dict): The post to refine
            user_feedback (str): User's feedback/requests
            
        Returns:
            dict: Refined post
        """
        print("🔧 Refining post based on your feedback...")
        
        # Generate refined version
        refined_post = self.post_generator.refine_with_feedback(
            post_data=post_data,
            user_feedback=user_feedback,
            brand_profile=self.brand_profile
        )
        
        # Regenerate image if needed
        if refined_post.get('caption') != post_data.get('caption'):
            print("🎨 Regenerating image...")
            image_path = self.image_generator.generate_background(
                post_data=refined_post,
                brand_profile=self.brand_profile,
                platform=post_data.get('platform', 'linkedin')
            )
            
            final_image_path = self.image_generator.add_text_overlay(
                image_path=image_path,
                text=refined_post.get('overlay_text', ''),
                brand_profile=self.brand_profile
            )
            
            refined_post['image_path'] = final_image_path
        
        print("✅ Post refinement complete!")
        return refined_post
    
    def save_post(self, post_data, output_dir="data/generated_posts"):
        """
        Save generated post to disk
        
        Args:
            post_data (dict): Post to save
            output_dir (str): Directory to save to
            
        Returns:
            str: Path to saved files
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"post_{timestamp}"
        
        # Save caption as text file
        caption_path = os.path.join(output_dir, f"{base_filename}_caption.txt")
        with open(caption_path, 'w', encoding='utf-8') as f:
            f.write(post_data['caption'])
        
        # Save metadata as JSON
        metadata_path = os.path.join(output_dir, f"{base_filename}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'platform': post_data.get('platform'),
                'intent': post_data.get('intent'),
                'timestamp': timestamp,
                'caption': post_data['caption'],
                'overlay_text': post_data.get('overlay_text', '')
            }, f, indent=2)
        
        print(f"💾 Post saved to {output_dir}")
        return output_dir


# Example usage (can be run directly for testing)
if __name__ == "__main__":
    # Initialize the agent
    agent = SocialMediaAgent()
    
    # Example: Analyze a brand
    brand_profile = agent.analyze_brand(
        website_url="https://example.com",
        existing_posts=[
            "Excited to announce our new AI hackathon! 🚀",
            "Join us for the biggest tech event of the year."
        ]
    )
    
    print("\nBrand Profile:", json.dumps(brand_profile, indent=2))
    
    # Example: Generate a post
    posts = agent.generate_post(
        intent="Announce AI hackathon with Super Bowl theme",
        platform="linkedin",
        constraints={
            'tone': 'exciting',
            'cta': 'Register now'
        }
    )
    
    print(f"\nGenerated {len(posts)} post variations!")