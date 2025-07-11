#!/usr/bin/env python3
"""
Setup script for Grok CLI - helps configure .env file
"""

import os
import shutil
from pathlib import Path

def setup_env_file():
    """Set up .env file from template"""
    env_example = Path('.env.example')
    env_file = Path('.env')
    
    print("🚀 Grok CLI Environment Setup")
    print("=" * 50)
    
    # Check if .env.example exists
    if not env_example.exists():
        print("❌ Error: .env.example file not found!")
        print("   This file should be in the project root.")
        return False
    
    # Check if .env already exists
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite not in ['y', 'yes']:
            print("Setup cancelled.")
            return False
    
    # Copy .env.example to .env
    try:
        shutil.copy2(env_example, env_file)
        print("✅ Created .env file from template")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
    
    # Help user configure the API key
    print("\n📝 Configuration:")
    print("   1. Get your API key from https://x.ai/api")
    print("   2. Edit .env file and replace 'your_grok_api_key_here' with your actual API key")
    print("   3. Optionally adjust other settings like temperature, max_tokens, etc.")
    
    # Ask if user wants to set API key now
    set_key_now = input("\nDo you want to set your API key now? (y/N): ").strip().lower()
    if set_key_now in ['y', 'yes']:
        api_key = input("Enter your Grok API key: ").strip()
        if api_key:
            try:
                # Read the .env file
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Replace the placeholder
                content = content.replace('your_grok_api_key_here', api_key)
                
                # Write it back
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print("✅ API key set successfully!")
            except Exception as e:
                print(f"❌ Error setting API key: {e}")
                print("   Please edit .env file manually")
        else:
            print("   No API key provided, please edit .env file manually")
    
    print("\n🎉 Setup complete!")
    print("   Next steps:")
    print("   1. Test configuration: python test_tools.py config")
    print("   2. Run basic tests: python test_tools.py basic")
    print("   3. Start CLI: grok-cli")
    
    return True

def check_requirements():
    """Check if requirements are installed"""
    try:
        import dotenv
        import composio_langchain
        import langchain
        import langchain_openai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("   Run: pip install -r requirements.txt")
        return False

def main():
    """Main setup function"""
    print("Grok CLI Setup Wizard")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Set up .env file
    if not setup_env_file():
        return
    
    # Final validation
    print("\n🔍 Validating setup...")
    try:
        from grok_cli.agent import GrokAgent
        # Try to create agent (will fail if API key is wrong, but that's ok)
        try:
            agent = GrokAgent()
            config = agent.get_config()
            print("✅ Agent can be initialized")
            print(f"   Model: {config['model']}")
            print(f"   API Key: {'Set' if config['api_key_set'] else 'Not set'}")
        except ValueError as e:
            if "GROK_API_KEY" in str(e):
                print("⚠️  API key not set in .env file")
                print("   Please edit .env file and add your API key")
            else:
                print(f"⚠️  Configuration issue: {e}")
    except ImportError as e:
        print(f"❌ Import error: {e}")
    
    print("\n🎊 Setup wizard complete!")
    print("   Your Grok CLI is ready to use!")

if __name__ == "__main__":
    main() 