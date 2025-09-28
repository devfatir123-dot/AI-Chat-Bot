"""
Quick Demo of AI ChatBot
Run this to test the chatbot functionality without the full interface
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from knowledge_base import KnowledgeBase
from ai_service import AIService

def demo_chatbot():
    print("🤖 AI ChatBot Demo")
    print("=" * 40)
    
    # Initialize components
    kb = KnowledgeBase()
    ai_service = AIService()
    
    # Test questions
    test_questions = [
        "Hello there!",
        "What can you help me with?", 
        "Can you calculate 15 + 25?",
        "Tell me about Python programming",
        "What is science?",
        "Thank you for your help",
        "Goodbye!"
    ]
    
    print("Testing with sample questions:\n")
    
    for question in test_questions:
        print(f"👤 User: {question}")
        
        # Try AI service first, then knowledge base
        ai_response = ai_service.get_free_ai_response(question)
        if ai_response:
            response = ai_response
            source = "AI Service"
        else:
            response = kb.get_response(question)
            source = "Knowledge Base"
        
        print(f"🤖 Bot ({source}): {response}")
        print("-" * 40)
    
    print("\n✅ Demo complete! The chatbot is working properly.")
    print("\nTo start the full chatbot:")
    print("• Command line: python chatbot.py")
    print("• Web interface: python web_app.py")

if __name__ == "__main__":
    try:
        demo_chatbot()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")