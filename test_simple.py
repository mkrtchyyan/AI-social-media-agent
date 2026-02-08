"""
Simple test script to verify setup
Run this to make sure everything is working before using the full UI
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_keys():
    """Test if API keys are set"""
    print("🔍 Checking API keys...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if openai_key:
        print(f"✅ OpenAI API key found: {openai_key[:10]}...")
    else:
        print("❌ OpenAI API key not found!")
        print("   Please add OPENAI_API_KEY to your .env file")
        return False
    
    return True


def test_imports():
    """Test if all required packages are installed"""
    print("\n🔍 Checking required packages...")
    
    packages = [
        ('openai', 'OpenAI'),
        ('PIL', 'Pillow'),
        ('requests', 'Requests'),
        ('bs4', 'BeautifulSoup4'),
        ('streamlit', 'Streamlit')
    ]
    
    all_good = True
    for package_import, package_name in packages:
        try:
            __import__(package_import)
            print(f"✅ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} not installed!")
            all_good = False
    
    return all_good


def test_directories():
    """Create necessary directories"""
    print("\n🔍 Setting up directories...")
    
    directories = [
        'data/generated_posts',
        'data/generated_images',
        'data/brand_assets'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created/verified: {directory}")
    
    return True


def test_simple_api_call():
    """Test a simple API call to verify connectivity"""
    print("\n🔍 Testing API connectivity...")
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API test successful!' and nothing else."}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("   Common issues:")
        print("   - Invalid API key")
        print("   - No credits remaining")
        print("   - Internet connection problem")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("AI SOCIAL MEDIA AGENT - SETUP TEST")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("API Keys", test_api_keys),
        ("Package Imports", test_imports),
        ("Directories", test_directories),
        ("API Connectivity", test_simple_api_call)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"TEST: {test_name}")
        print('=' * 50)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to go!")
        print("\nRun the app with:")
        print("  cd frontend")
        print("  streamlit run app.py")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        print("\nNeed help?")
        print("1. Make sure .env file exists with OPENAI_API_KEY")
        print("2. Run: pip install -r requirements.txt")
        print("3. Check OpenAI API key at https://platform.openai.com/api-keys")