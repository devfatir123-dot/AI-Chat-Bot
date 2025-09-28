"""
Quick Interactive Test - Shows the improved AI responses
"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from ai_service import AIService

def test_responses():
    ai = AIService()
    
    test_inputs = [
        "Hello!",
        "What can you do?", 
        "Calculate 25 + 15",
        "What is Python?",
        "Tell me about physics",
        "How are you?",
        "What is machine learning?",
        "Thank you",
        "Can you help me with math?",
        "Goodbye"
    ]
    
    print("🤖 Testing Improved AI Responses")
    print("=" * 50)
    
    for question in test_inputs:
        response = ai.get_free_ai_response(question)
        print(f"\n👤 User: {question}")
        print(f"🤖 Bot: {response}")
        print("-" * 30)

if __name__ == "__main__":
    test_responses()