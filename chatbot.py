import os
import sys
import json
import time
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from knowledge_base import KnowledgeBase
from ai_service import AIService

class ChatBot:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.ai_service = AIService()
        self.conversation_history = []
        self.user_name = "User"
        
    def setup_nltk(self):
        """Download required NLTK data"""
        try:
            import nltk
            print(f"{Fore.YELLOW}Setting up language processing...")
            
            # Try to download required NLTK data
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
                print(f"{Fore.GREEN}✓ Language processing setup complete!")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Some language features may be limited: {e}")
                
        except ImportError:
            print(f"{Fore.YELLOW}⚠ Advanced language processing not available")
    
    def get_user_name(self):
        """Get user's name for personalization"""
        while True:
            name = input(f"{Fore.CYAN}What's your name? (or press Enter for 'User'): {Style.RESET_ALL}").strip()
            if name:
                self.user_name = name
                break
            else:
                self.user_name = "User"
                break
        
        print(f"{Fore.GREEN}Nice to meet you, {self.user_name}! 🤖")
    
    def save_conversation(self):
        """Save conversation history to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "user_name": self.user_name,
                "messages": self.conversation_history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            print(f"{Fore.GREEN}✓ Conversation saved to {filename}")
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error saving conversation: {e}")
    
    def get_response(self, user_input):
        """Get the best available response for user input"""
        
        # First, try AI services if available
        ai_response = self.ai_service.get_groq_response(user_input)
        if ai_response:
            return ai_response, "Groq"
        
        ai_response = self.ai_service.get_huggingface_response(user_input)
        if ai_response:
            return ai_response, "Hugging Face"
        
        ai_response = self.ai_service.get_free_ai_response(user_input)
        if ai_response:
            return ai_response, "AI Service"
        
        # Fall back to knowledge base
        kb_response = self.knowledge_base.get_response(user_input)
        return kb_response, "Knowledge Base"
    
    def print_welcome(self):
        """Print welcome message"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🤖 Welcome to AI ChatBot! 🤖")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}I'm an AI assistant ready to help you with:")
        print(f"{Fore.GREEN}  • General questions and knowledge")
        print(f"{Fore.GREEN}  • Programming and technology")
        print(f"{Fore.GREEN}  • Math and science topics")
        print(f"{Fore.GREEN}  • And much more!")
        print(f"{Fore.WHITE}\nCommands:")
        print(f"{Fore.YELLOW}  • Type 'quit', 'exit', or 'bye' to end the conversation")
        print(f"{Fore.YELLOW}  • Type 'save' to save our conversation")
        print(f"{Fore.YELLOW}  • Type 'help' to see what I can do")
        print(f"{Fore.CYAN}{'='*60}\n")
    
    def start_chat(self):
        """Main chat loop"""
        self.setup_nltk()
        self.print_welcome()
        self.get_user_name()
        
        print(f"{Fore.MAGENTA}ChatBot: Hello {self.user_name}! How can I help you today? 🚀")
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Fore.CYAN}{self.user_name}: {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Check for special commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    response, source = self.knowledge_base.get_response(user_input), "Knowledge Base"
                    print(f"{Fore.MAGENTA}ChatBot: {response}")
                    
                    # Ask if user wants to save conversation
                    if self.conversation_history:
                        save_choice = input(f"{Fore.YELLOW}Would you like to save our conversation? (y/n): {Style.RESET_ALL}").strip().lower()
                        if save_choice in ['y', 'yes']:
                            self.save_conversation()
                    
                    break
                
                elif user_input.lower() == 'save':
                    self.save_conversation()
                    continue
                
                # Record user message
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "sender": self.user_name,
                    "message": user_input
                })
                
                # Get response
                print(f"{Fore.YELLOW}🤔 Thinking...")
                response, source = self.get_response(user_input)
                
                # Display response with source indicator
                source_color = {
                    "Groq": Fore.BLUE,
                    "Hugging Face": Fore.GREEN,
                    "AI Service": Fore.CYAN,
                    "Knowledge Base": Fore.MAGENTA
                }.get(source, Fore.MAGENTA)
                
                print(f"{source_color}ChatBot ({source}): {response}")
                
                # Record bot response
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "sender": "ChatBot",
                    "message": response,
                    "source": source
                })
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Chat interrupted by user.")
                if self.conversation_history:
                    save_choice = input(f"{Fore.YELLOW}Would you like to save our conversation? (y/n): {Style.RESET_ALL}").strip().lower()
                    if save_choice in ['y', 'yes']:
                        self.save_conversation()
                break
                
            except Exception as e:
                print(f"{Fore.RED}An error occurred: {e}")
                print(f"{Fore.YELLOW}Let's continue our conversation...")

def main():
    """Main function to run the chatbot"""
    try:
        chatbot = ChatBot()
        chatbot.start_chat()
    except Exception as e:
        print(f"{Fore.RED}Error starting chatbot: {e}")
        print(f"{Fore.YELLOW}Please make sure all dependencies are installed.")
        print(f"{Fore.YELLOW}Run: pip install -r requirements.txt")

if __name__ == "__main__":
    main()