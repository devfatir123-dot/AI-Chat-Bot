"""
Interactive Command Line Test for AI ChatBot
This allows you to test the chatbot quickly without the full setup
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from knowledge_base import KnowledgeBase
from ai_service import AIService

def quick_test():
    print("🤖 Quick ChatBot Test")
    print("=" * 40)
    print("Type 'quit' to exit\n")
    
    # Initialize components
    kb = KnowledgeBase()
    ai_service = AIService()
    
    def get_response(user_input):
        """Get the best available response"""
        # Try AI service first
        ai_response = ai_service.get_free_ai_response(user_input)
        if ai_response:
            return ai_response, "AI Service"
        
        # Fall back to knowledge base
        kb_response = kb.get_response(user_input)
        return kb_response, "Knowledge Base"
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Bot: Goodbye! Thanks for testing the chatbot! 👋")
                break
            
            response, source = get_response(user_input)
            print(f"Bot ({source}): {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nBot: Goodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    quick_test()