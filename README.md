# AI Social Media Agent 🚀

Automated, brand-aware content creation for LinkedIn & Instagram using AI.

## Features

- 🎯 **Brand Analysis**: Learns your brand voice from website and existing posts
- ✍️ **Multi-Variation Generation**: Creates 3 unique post variations per request
- 🔄 **Self-Improvement Loop**: AI critiques and refines its own outputs
- 🎨 **Custom Images**: Generates brand-aligned images with text overlays
- 👤 **Human-in-the-Loop**: Easy refinement based on your feedback

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get OpenAI API Key (FREE $5 Credits!)

1. Go to https://platform.openai.com/
2. Sign up (new accounts get $5 free credits)
3. Navigate to "API Keys"
4. Click "Create new secret key"
5. Copy your key

### 3. Set Up API Key

Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Then edit `.env` and add your API key:
```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Test Setup
```bash
python test_simple.py
```

All tests should pass ✅

### 5. Run the App
```bash
cd frontend
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure
```
social-media-agent/
├── backend/
│   ├── app.py                 # Main orchestration
│   ├── brand_analyzer.py      # Brand voice extraction (GPT-4)
│   ├── post_generator.py      # Post caption generation (GPT-4)
│   ├── feedback_loop.py       # AI self-critique system (GPT-4)
│   └── image_generator.py     # Image creation (DALL-E)
├── frontend/
│   └── app.py                 # Streamlit UI
├── data/
│   ├── generated_posts/       # Exported posts
│   └── generated_images/      # Generated images
├── requirements.txt           # Python dependencies
├── .env                       # Your API key (DON'T commit!)
├── .env.example              # Template
└── README.md
```

## Usage Flow

1. **Analyze Brand** (Tab 1)
   - Enter company website URL
   - Paste 3-5 existing social posts
   - Optionally add brand guidelines
   - Click "Analyze Brand"

2. **Generate Posts** (Tab 2)
   - Enter what the post should be about
   - Select platform (LinkedIn/Instagram)
   - Add optional constraints or elements
   - Click "Generate Posts"
   - Review 3 variations and select one

3. **Review & Refine** (Tab 3)
   - View selected post
   - Provide feedback for improvements
   - Use quick actions or custom feedback
   - Refine until perfect

4. **Export** (Tab 4)
   - Copy caption and hashtags
   - Download image
   - Save to disk or export as JSON

## Example Use Cases

### Hackathon Announcement
```
Intent: "Announce our AI hackathon with Super Bowl theme"
Platform: LinkedIn
Elements: Speakers, prizes, registration link
```

### Product Launch
```
Intent: "Introduce our new AI-powered analytics tool"
Platform: LinkedIn
Tone: Professional and exciting
```

### Partnership Announcement
```
Intent: "Announce partnership with major tech company"
Platform: Both
Include: Partner logo, collaboration details
```

## API Costs (with OpenAI)

**GPT-4:**
- Brand analysis: ~$0.08 per analysis
- Post generation: ~$0.12 per 3 variations
- Feedback loops: ~$0.08 per iteration

**DALL-E 3:**
- Image generation: ~$0.04 per image

**Estimated cost per complete post:** $0.30 - $0.50

**With $5 free credits:** You can create ~10-15 complete posts!

## Troubleshooting

### API Key Errors
- Make sure `.env` file is in the root directory
- Check that API key starts with `sk-`
- Verify you have credits at https://platform.openai.com/account/usage
- Don't commit `.env` to version control

### Image Generation Fails
- Check OpenAI API credits
- Verify internet connection
- System will create placeholder if DALL-E fails

### Brand Analysis Returns Generic Results
- Provide more existing posts (5-10 is ideal)
- Include website URL with substantial content
- Add explicit brand guidelines

### "Module not found" errors
- Make sure `backend/__init__.py` exists
- Run commands from the root folder
- Run `pip install -r requirements.txt` again

## Model Information

This project uses:
- **GPT-4 Turbo** for text generation (brand analysis, posts, feedback)
- **DALL-E 3** for image generation

## Future Features

- [ ] Video post support
- [ ] Multi-platform adaptation
- [ ] Content calendar integration
- [ ] A/B testing suggestions
- [ ] Analytics integration

## License

MIT License - feel free to use for your hackathon!

## Support

For issues or questions, create an issue in the repository.

