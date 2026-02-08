"""
Image Generator Module
Generates background images and adds text overlays
"""

import openai
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import os
from datetime import datetime


class ImageGenerator:
    """
    Generates images for social media posts
    """
    
    def __init__(self, openai_api_key):
        """
        Initialize the image generator with OpenAI API
        
        Args:
            openai_api_key (str): API key for OpenAI (DALL-E)
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        
        # Create directory for generated images
        self.output_dir = "data/generated_images"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_background(self, post_data, brand_profile, platform):
        """
        Generate a background image using DALL-E
        
        Args:
            post_data (dict): Post data with image description
            brand_profile (dict): Brand profile with colors and style
            platform (str): Social platform (determines dimensions)
            
        Returns:
            str: Path to generated image
        """
        # Get platform-specific dimensions
        dimensions = self._get_image_dimensions(platform)
        
        # Build DALL-E prompt
        dalle_prompt = self._build_dalle_prompt(post_data, brand_profile, platform)
        
        try:
            print(f"🎨 Generating image with DALL-E 3...")
            
            # Call DALL-E API
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=dalle_prompt,
                size=dimensions,
                quality="standard",
                n=1
            )
            
            # Get image URL
            image_url = response.data[0].url
            
            # Download image
            image_response = requests.get(image_url)
            image = Image.open(io.BytesIO(image_response.content))
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bg_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            image.save(filepath)
            
            print(f"✅ Image saved to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"⚠️ Image generation error: {e}")
            # Return a placeholder image path
            return self._create_placeholder_image(dimensions, brand_profile)
    
    def _build_dalle_prompt(self, post_data, brand_profile, platform):
        """
        Build prompt for DALL-E image generation
        
        Args:
            post_data (dict): Post data
            brand_profile (dict): Brand profile
            platform (str): Social platform
            
        Returns:
            str: DALL-E prompt
        """
        # Extract brand colors
        colors = brand_profile['visual_identity'].get('primary_colors', ['#1a73e8'])
        color_names = self._hex_to_color_names(colors)
        
        # Extract design style
        design_style = brand_profile['visual_identity'].get('design_style', 'modern')
        
        # Get image description from post
        image_desc = post_data.get('image_description', 'professional tech background')
        
        # Build comprehensive prompt
        prompt = f"""
Create a professional social media background image for {platform}.

Style: {design_style}, clean, modern
Colors: Use {', '.join(color_names)} as primary colors
Theme: {image_desc}

Requirements:
- Leave space in the center or top for text overlay
- High quality, professional look
- Suitable for corporate social media
- No text or words in the image
- Clean composition with good contrast
- Should look good on mobile devices

Make it visually appealing but not too busy - text will be overlaid on this image.
"""
        
        return prompt
    
    def _get_image_dimensions(self, platform):
        """
        Get appropriate image dimensions for platform
        
        Args:
            platform (str): Social platform
            
        Returns:
            str: Dimensions in OpenAI format
        """
        # DALL-E 3 supports: 1024x1024, 1792x1024, 1024x1792
        dimensions = {
            "linkedin": "1792x1024",  # Landscape for LinkedIn
            "instagram": "1024x1024"  # Square for Instagram
        }
        
        return dimensions.get(platform, "1024x1024")
    
    def add_text_overlay(self, image_path, text, brand_profile):
        """
        Add text overlay to image
        
        Args:
            image_path (str): Path to background image
            text (str): Text to overlay
            brand_profile (dict): Brand profile with colors
            
        Returns:
            str: Path to image with text overlay
        """
        try:
            print(f"✍️ Adding text overlay...")
            
            # Open image
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            
            # Get image dimensions
            img_width, img_height = image.size
            
            # Try to load a nice font, fall back to default (cross-platform)
            font_size = int(img_width * 0.08)  # 8% of image width
            font = None
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                "C:/Windows/Fonts/arialbd.ttf",  # Windows
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                        break
                    except Exception:
                        continue
            if font is None:
                font = ImageFont.load_default()
            
            # Calculate text position (centered, upper third of image)
            # Use textbbox for accurate text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (img_width - text_width) // 2
            y = img_height // 3
            
            # Add text shadow for better readability
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill='black')
            
            # Draw main text in white (or brand color if light background)
            draw.text((x, y), text, font=font, fill='white')
            
            # Save with overlay
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"final_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            image.save(filepath)
            
            print(f"✅ Text overlay added: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"⚠️ Text overlay error: {e}")
            # Return original image if overlay fails
            return image_path
            