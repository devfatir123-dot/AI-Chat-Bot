#!/usr/bin/env python3
"""
Quick setup script for AI ChatBot
This script helps users get started quickly by installing dependencies
and providing setup guidance.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🤖 AI ChatBot Setup Script 🤖")
    print("=" * 60)
    print("Setting up your AI chatbot environment...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Python 3.7 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again.")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible!")
        return True

def install_requirements():
    """Install required packages"""
    try:
        print("📦 Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error installing packages!")
        print("   Try running: pip install -r requirements.txt")
        return False

def setup_nltk_data():
    """Download required NLTK data"""
    try:
        print("📚 Setting up natural language processing...")
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("✅ Language processing setup complete!")
        return True
    except Exception as e:
        print(f"⚠️  Warning: NLTK setup failed: {e}")
        print("   The chatbot will still work with reduced functionality.")
        return False

def show_usage_instructions():
    """Show how to use the chatbot"""
    print("\n" + "=" * 60)
    print("🚀 Setup Complete! Here's how to use your chatbot:")
    print("=" * 60)
    
    print("\n1. 💬 Command Line Interface:")
    print("   python chatbot.py")
    
    print("\n2. 🌐 Web Interface:")
    print("   python web_app.py")
    print("   Then open: http://localhost:5000")
    
    print("\n3. 🔑 Optional - Add AI API Keys:")
    print("   Edit the .env file and add your API keys for enhanced responses")
    
    print("\n4. 📖 Need Help?")
    print("   Check README.md for detailed instructions")
    
    print("\n" + "=" * 60)
    print("Happy chatting! 🤖✨")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return
    
    # Install requirements
    if not install_requirements():
        input("\nPress Enter to exit...")
        return
    
    # Setup NLTK data
    setup_nltk_data()
    
    # Show usage instructions
    show_usage_instructions()
    
    # Ask user what they want to do
    print("\nWhat would you like to do now?")
    print("1. Start command-line chatbot")
    print("2. Start web interface")
    print("3. Exit setup")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\n🚀 Starting command-line chatbot...")
            try:
                import chatbot
                chatbot.main()
            except Exception as e:
                print(f"❌ Error starting chatbot: {e}")
            break
            
        elif choice == '2':
            print("\n🌐 Starting web interface...")
            print("📱 Open your browser and go to: http://localhost:5000")
            try:
                import web_app
                # This will start the Flask app
            except Exception as e:
                print(f"❌ Error starting web interface: {e}")
            break
            
        elif choice == '3':
            print("\n👋 Setup complete! Run the chatbot anytime using the commands above.")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        input("Press Enter to exit...")