"""
Streamlit Frontend for AI Social Media Agent
This provides an easy-to-use interface for the entire workflow
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime

# Add project root to path
_project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(_project_root))

from backend.app import SocialMediaAgent

# Page configuration
st.set_page_config(
    page_title="AI Social Media Agent",
    page_icon="🚀",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'brand_profile' not in st.session_state:
    st.session_state.brand_profile = None
if 'generated_posts' not in st.session_state:
    st.session_state.generated_posts = []
if 'selected_post' not in st.session_state:
    st.session_state.selected_post = None


def initialize_agent():
    """Initialize the AI agent with API keys"""
    try:
        agent = SocialMediaAgent()
        st.session_state.agent = agent
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        st.info("Make sure you have set OPENAI_API_KEY in your .env file")
        return False


def main():
    """Main Streamlit application"""
    
    # Title and description
    st.title("🚀 AI Social Media Agent")
    st.markdown("""
    Create **brand-aligned** social media posts for LinkedIn & Instagram automatically!
    
    This AI agent:
    - 🎯 Learns your brand voice and visual identity
    - ✍️ Generates multiple post variations
    - 🔄 Self-improves through AI feedback loops
    - 🎨 Creates custom images with text overlays
    """)
    
    st.divider()
    
    # Sidebar for API key setup
    with st.sidebar:
        st.header("⚙️ Setup")
        
        st.markdown("""
        **Required API Key:**
        - OpenAI API Key (for GPT-4 + DALL-E)
        
        Add this to a `.env` file in the root directory:
            OPENAI_API_KEY=your_key_here
            **Get your free API key:**
        1. Go to https://platform.openai.com/
        2. Sign up (you get $5 free credits!)
        3. Go to API Keys section
        4. Create new key
        5. Copy and paste into .env file
        """)
        
        if st.button("🔌 Initialize Agent"):
            with st.spinner("Initializing AI agent..."):
                if initialize_agent():
                    st.success("✅ Agent initialized!")
                else:
                    st.error("❌ Initialization failed")
        
        st.divider()
        
        # Quick tips
        st.markdown("""
        **💡 Tips:**
        - Start by analyzing your brand
        - Generate multiple variations
        - Refine based on AI feedback
        - Download your favorites
        
        **💰 Cost per post:** ~$0.50
        **Free credits:** $5 = ~10 complete posts
        """)
    
    # Main content area
    if st.session_state.agent is None:
        st.warning("👈 Please initialize the agent using the sidebar")
        return
    
    # Create tabs for different steps
    tab1, tab2, tab3, tab4 = st.tabs([
        "1️⃣ Brand Analysis", 
        "2️⃣ Generate Posts", 
        "3️⃣ Review & Refine",
        "4️⃣ Export"
    ])
    
    # TAB 1: Brand Analysis
    with tab1:
        st.header("📊 Brand Analysis")
        st.markdown("Let's understand your brand voice and visual identity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Input Brand Materials")
            
            # Website URL
            website_url = st.text_input(
                "Company Website URL",
                placeholder="https://example.com",
                help="We'll analyze the content to understand your brand"
            )
            
            # Existing posts
            st.markdown("**Existing Social Media Posts** (one per line)")
            existing_posts_text = st.text_area(
                "Paste 3-5 existing posts",
                height=200,
                placeholder="Excited to announce our new product! 🚀\n\nJoin us for our upcoming webinar...\n\n..."
            )
            
            # Parse posts
            existing_posts = [p.strip() for p in existing_posts_text.split('\n') if p.strip()]
            
            # Optional brand guidelines
            with st.expander("➕ Add Brand Guidelines (Optional)"):
                brand_tone = st.selectbox(
                    "Brand Tone",
                    ["Professional", "Casual", "Playful", "Inspirational", "Technical"]
                )
                
                brand_colors = st.text_input(
                    "Brand Colors (comma-separated hex codes)",
                    placeholder="#1a73e8, #34a853"
                )
                
                # Build guidelines dict
                brand_guidelines = None
                if brand_colors:
                    brand_guidelines = {
                        "tone": brand_tone.lower(),
                        "colors": [c.strip() for c in brand_colors.split(',')]
                    }
        
        with col2:
            st.subheader("Brand Profile")
            
            if st.button("🔍 Analyze Brand", type="primary", use_container_width=True):
                if not website_url and not existing_posts:
                    st.error("Please provide at least a website URL or existing posts")
                else:
                    with st.spinner("Analyzing your brand... This may take 30-60 seconds"):
                        brand_profile = st.session_state.agent.analyze_brand(
                            website_url=website_url if website_url else None,
                            existing_posts=existing_posts if existing_posts else None,
                            brand_guidelines=brand_guidelines
                        )
                        st.session_state.brand_profile = brand_profile
                        st.success("✅ Brand analysis complete!")
            
            # Display brand profile if available
            if st.session_state.brand_profile:
                st.json(st.session_state.brand_profile, expanded=False)
                
                # Show key insights
                st.markdown("**Key Insights:**")
                profile = st.session_state.brand_profile
                st.write(f"- **Tone:** {profile['brand_voice']['tone']}")
                st.write(f"- **Emoji Usage:** {profile['brand_voice']['emoji_usage']}")
                st.write(f"- **Design Style:** {profile['visual_identity']['design_style']}")
                st.write(f"- **Key Themes:** {', '.join(profile['messaging_patterns']['key_themes'][:3])}")
    
    # TAB 2: Generate Posts
    with tab2:
        st.header("✍️ Generate Social Media Posts")
        
        if not st.session_state.brand_profile:
            st.warning("⚠️ Please analyze your brand first (Tab 1)")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Post Configuration")
            
            # Post intent
            intent = st.text_input(
                "What is this post about?",
                placeholder="Announce our AI hackathon with Super Bowl theme",
                help="Be specific about what you want to communicate"
            )
            
            # Platform selection
            platform = st.selectbox(
                "Platform",
                ["linkedin", "instagram"],
                format_func=lambda x: x.capitalize()
            )
            
            # Optional constraints
            with st.expander("⚙️ Additional Constraints (Optional)"):
                tone_override = st.selectbox(
                    "Tone Override",
                    ["Use Brand Default", "More Formal", "More Casual", "More Exciting", "More Urgent"]
                )
                
                cta_text = st.text_input(
                    "Specific CTA",
                    placeholder="Register now",
                    help="Leave empty to use brand defaults"
                )
                
                post_date = st.date_input("Post Date (Optional)")
                
                # Build constraints
                constraints = {}
                if tone_override != "Use Brand Default":
                    constraints['tone'] = tone_override.lower().replace("more ", "")
                if cta_text:
                    constraints['cta'] = cta_text
                if post_date:
                    constraints['date'] = str(post_date)
            
            # RAG elements (e.g., speaker names, prizes)
            with st.expander("📎 Elements to Include (Optional)"):
                st.markdown("Add specific information to include in the post")
                
                speakers = st.text_input("Speaker Names", placeholder="John Doe, Jane Smith")
                prizes = st.text_input("Prize Information", placeholder="$10,000 grand prize")
                event_details = st.text_area("Event Details", placeholder="Date, time, location...")
                
                # Build RAG elements
                rag_elements = {}
                if speakers:
                    rag_elements['speakers'] = speakers
                if prizes:
                    rag_elements['prizes'] = prizes
                if event_details:
                    rag_elements['event_details'] = event_details
        
        with col2:
            st.subheader("Generated Variations")
            
            if st.button("🎨 Generate Posts", type="primary", use_container_width=True):
                if not intent:
                    st.error("Please provide a post intent")
                else:
                    with st.spinner("Generating 3 post variations... This may take 2-3 minutes"):
                        try:
                            posts = st.session_state.agent.generate_post(
                                intent=intent,
                                platform=platform,
                                constraints=constraints if constraints else None,
                                rag_elements=rag_elements if rag_elements else None
                            )
                            st.session_state.generated_posts = posts
                            st.success(f"✅ Generated {len(posts)} variations!")
                        except Exception as e:
                            st.error(f"Error generating posts: {e}")
                            st.info("Check your OpenAI API key and credits")
            
            # Display generated posts
            if st.session_state.generated_posts:
                st.markdown(f"**{len(st.session_state.generated_posts)} variations generated**")
                
                for idx, post in enumerate(st.session_state.generated_posts):
                    with st.expander(f"📄 Variation {idx + 1} (Score: {post.get('critique_score', 'N/A')}/10)"):
                        st.markdown("**Caption:**")
                        st.write(post['caption'])
                        
                        st.markdown("**Overlay Text:**")
                        st.code(post.get('overlay_text', ''))
                        
                        st.markdown("**Hashtags:**")
                        st.write(' '.join([f"#{tag}" for tag in post.get('hashtags', [])]))
                        
                        # Show image if available
                        if 'image_path' in post and os.path.exists(post['image_path']):
                            st.image(post['image_path'], use_container_width=True)
                        
                        # Select button
                        if st.button(f"✅ Select Variation {idx + 1}", key=f"select_{idx}"):
                            st.session_state.selected_post = post
                            st.success(f"Selected Variation {idx + 1}!")
    
    # TAB 3: Review & Refine
    with tab3:
        st.header("🔧 Review & Refine")
        
        if not st.session_state.selected_post:
            st.info("👈 Generate and select a post variation from Tab 2")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Current Post")
            
            post = st.session_state.selected_post
            
            st.markdown("**Caption:**")
            st.write(post['caption'])
            
            st.markdown("**Overlay Text:**")
            st.code(post.get('overlay_text', ''))
            
            st.markdown("**Hashtags:**")
            st.write(' '.join([f"#{tag}" for tag in post.get('hashtags', [])]))
            
            # Show image
            if 'image_path' in post and os.path.exists(post['image_path']):
                st.image(post['image_path'], use_container_width=True)
        
        with col2:
            st.subheader("Refinement")
            
            st.markdown("**Provide feedback to improve this post:**")
            
            user_feedback = st.text_area(
                "What would you like to change?",
                placeholder="Make it more exciting\nAdd a stronger CTA\nShorten the caption\nChange the tone to be more professional",
                height=150
            )
            
            if st.button("🔄 Refine Post", type="primary", use_container_width=True):
                if not user_feedback:
                    st.error("Please provide feedback")
                else:
                    with st.spinner("Refining post based on your feedback..."):
                        try:
                            refined_post = st.session_state.agent.refine_post(
                                post_data=post,
                                user_feedback=user_feedback
                            )
                            st.session_state.selected_post = refined_post
                            st.success("✅ Post refined!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error refining post: {e}")
            
            # Quick action buttons
            st.markdown("**Quick Actions:**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("📝 Shorten", use_container_width=True):
                    with st.spinner("Shortening..."):
                        try:
                            refined = st.session_state.agent.refine_post(
                                post, "Make the caption shorter and more concise"
                            )
                            st.session_state.selected_post = refined
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            with col_b:
                if st.button("🎯 Stronger CTA", use_container_width=True):
                    with st.spinner("Improving CTA..."):
                        try:
                            refined = st.session_state.agent.refine_post(
                                post, "Make the call-to-action more compelling and urgent"
                            )
                            st.session_state.selected_post = refined
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
    
    # TAB 4: Export
    with tab4:
        st.header("💾 Export Your Posts")
        
        if not st.session_state.selected_post:
            st.info("Select a post from Tab 3 to export")
            return
        
        post = st.session_state.selected_post
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Final Post Preview")
            
            st.markdown("**Caption:**")
            caption_text = post['caption']
            st.text_area("Copy Caption", caption_text, height=200, key="export_caption")
            
            st.markdown("**Hashtags:**")
            hashtags_text = ' '.join([f"#{tag}" for tag in post.get('hashtags', [])])
            st.text_input("Copy Hashtags", hashtags_text, key="export_hashtags")
            
            # Show final image
            if 'image_path' in post and os.path.exists(post['image_path']):
                st.image(post['image_path'], use_container_width=True)
                
                # Download image button
                with open(post['image_path'], 'rb') as f:
                    st.download_button(
                        label="📥 Download Image",
                        data=f,
                        file_name=f"social_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
        
        with col2:
            st.subheader("Actions")
            
            # Save to disk
            if st.button("💾 Save to Disk", use_container_width=True):
                output_dir = st.session_state.agent.save_post(post)
                st.success(f"✅ Saved to {output_dir}")
            
            # Export as JSON
            if st.button("📄 Export as JSON", use_container_width=True):
                json_data = json.dumps(post, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            st.divider()
            
            # Post metadata
            st.markdown("**Post Metadata:**")
            st.write(f"Platform: {post.get('platform', 'N/A').capitalize()}")
            st.write(f"Intent: {post.get('intent', 'N/A')}")
            if 'critique_score' in post:
                st.write(f"Quality Score: {post['critique_score']}/10")
            
            st.divider()
            
            # Start over
            if st.button("🔄 Generate New Post", use_container_width=True):
                st.session_state.generated_posts = []
                st.session_state.selected_post = None
                st.success("Ready for a new post!")
                st.rerun()


if __name__ == "__main__":
    main()