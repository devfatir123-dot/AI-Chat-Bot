import os
import json
import requests
from dotenv import load_dotenv

class AIService:
    def __init__(self):
        load_dotenv()
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY')
        
    def get_groq_response(self, prompt, max_tokens=150):
        """Get response from Groq API (requires API key)"""
        if not self.groq_api_key or self.groq_api_key == 'your_groq_api_key_here':
            return None
        
        try:
            from groq import Groq
            
            # Initialize Groq client
            client = Groq(api_key=self.groq_api_key)
            
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Current Groq model
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Provide concise and accurate answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else ""
            
        except ImportError:
            print("Groq library not available. Install with: pip install groq")
            return None
        except Exception as e:
            print(f"Groq API Error: {e}")
            return None
    
    def get_huggingface_response(self, prompt):
        """Get response from Hugging Face API (requires API key)"""
        if not self.huggingface_api_key or self.huggingface_api_key == 'your_huggingface_api_key_here':
            return None
        
        try:
            API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
            headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
            
            return None
            
        except Exception as e:
            print(f"Hugging Face API Error: {e}")
            return None
    
    def get_free_ai_response(self, prompt):
        """Get response using free AI services (no API key required)"""
        try:
            prompt_lower = prompt.lower()
            
            # Greetings
            if any(word in prompt_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
                return "Hello! I'm here to help you with questions, math, programming, and more. What would you like to know?"
            
            # Goodbyes
            if any(word in prompt_lower for word in ['bye', 'goodbye', 'see you', 'farewell']):
                return "Goodbye! It was nice chatting with you. Feel free to come back anytime you have questions!"
            
            # Thanks
            if any(word in prompt_lower for word in ['thank you', 'thanks', 'appreciate']):
                return "You're very welcome! I'm happy I could help. Is there anything else you'd like to know?"
            
            # Math questions - improved
            if any(word in prompt_lower for word in ['calculate', 'math', '+', '-', '*', '/', 'equals', 'plus', 'minus', 'times', 'divided']):
                try:
                    import re
                    # Look for mathematical expressions
                    math_expr = re.search(r'[\d\s+\-*/().]+', prompt)
                    if math_expr:
                        safe_chars = set('0123456789+-*/(). ')
                        expr = math_expr.group().strip()
                        if expr and all(c in safe_chars for c in expr):
                            try:
                                result = eval(expr)
                                return f"The calculation {expr} = {result}"
                            except:
                                pass
                    
                    # Handle word problems
                    if 'plus' in prompt_lower or 'add' in prompt_lower:
                        numbers = re.findall(r'\d+', prompt)
                        if len(numbers) >= 2:
                            result = sum(int(n) for n in numbers[:2])
                            return f"Adding {numbers[0]} + {numbers[1]} = {result}"
                    
                    return "I can help with math! Try asking something like '25 + 15' or 'calculate 10 * 5'"
                except:
                    return "I can help with basic math calculations. Try writing the expression clearly like '25 + 15' or '10 * 3'"
            
            # Programming questions - much more detailed
            if any(word in prompt_lower for word in ['python', 'code', 'programming', 'function', 'variable', 'loop', 'if', 'javascript', 'html', 'css']):
                if 'python' in prompt_lower:
                    if 'function' in prompt_lower:
                        return "In Python, you create functions with 'def'. For example:\n\ndef greet(name):\n    return f'Hello, {name}!'\n\nWhat specific aspect of Python functions would you like to know?"
                    elif 'loop' in prompt_lower:
                        return "Python has two main loops:\n• for loop: for item in list:\n• while loop: while condition:\n\nWhat type of loop are you interested in?"
                    elif 'variable' in prompt_lower:
                        return "In Python, variables are simple: name = 'John', age = 25, is_student = True. Python automatically detects the type!"
                    else:
                        return "Python is a versatile programming language! Are you interested in basics, functions, loops, data structures, or something specific?"
                elif 'javascript' in prompt_lower:
                    return "JavaScript is great for web development! It runs in browsers and servers. What aspect interests you - basics, functions, DOM manipulation, or frameworks?"
                elif 'html' in prompt_lower:
                    return "HTML structures web pages with tags like <div>, <p>, <h1>. What HTML concept would you like to learn about?"
                elif 'css' in prompt_lower:
                    return "CSS styles web pages! You can change colors, layouts, fonts and more. What CSS topic interests you?"
                else:
                    return "Programming is exciting! Which language or concept would you like to explore - Python, JavaScript, HTML, CSS, or something else?"
            
            # Science questions - more detailed
            if any(word in prompt_lower for word in ['science', 'physics', 'chemistry', 'biology', 'astronomy', 'atoms', 'molecules']):
                if 'physics' in prompt_lower:
                    return "Physics studies matter, energy, and motion! Topics include mechanics, electricity, magnetism, and quantum physics. What physics concept interests you?"
                elif 'chemistry' in prompt_lower:
                    return "Chemistry explores atoms, molecules, and reactions! It covers elements, compounds, acids, bases, and chemical bonds. What would you like to know?"
                elif 'biology' in prompt_lower:
                    return "Biology studies living things - cells, genetics, evolution, ecosystems, and how life works! What biological topic interests you?"
                elif 'astronomy' in prompt_lower:
                    return "Astronomy explores space - planets, stars, galaxies, and the universe! Are you curious about our solar system, distant galaxies, or something specific?"
                else:
                    return "Science is amazing! It helps us understand the world. Which field interests you - physics, chemistry, biology, astronomy, or earth science?"
            
            # Technology questions
            if any(word in prompt_lower for word in ['computer', 'technology', 'internet', 'ai', 'artificial intelligence', 'machine learning']):
                if 'ai' in prompt_lower or 'artificial intelligence' in prompt_lower:
                    return "AI is technology that makes computers smart! It includes machine learning, neural networks, and automation. What aspect of AI interests you?"
                elif 'machine learning' in prompt_lower:
                    return "Machine learning teaches computers to learn patterns from data without explicit programming. It's used in recommendations, image recognition, and predictions!"
                else:
                    return "Technology shapes our world! From computers and smartphones to AI and the internet. What technology topic would you like to explore?"
            
            # Education questions
            if any(word in prompt_lower for word in ['learn', 'study', 'education', 'school', 'university', 'homework']):
                return "Learning is wonderful! I can help explain concepts in math, science, programming, and more. What subject would you like to study?"
            
            # Help questions
            if any(word in prompt_lower for word in ['help', 'what can you do', 'capabilities', 'features']):
                return "I can help with:\n• Math calculations and problems\n• Programming concepts (Python, JavaScript, etc.)\n• Science topics (physics, chemistry, biology)\n• General knowledge and explanations\n• Technology questions\n\nWhat would you like to explore?"
            
            # Time/Date questions  
            if any(word in prompt_lower for word in ['time', 'date', 'day', 'today', 'now']):
                return "I don't have access to real-time data, but you can check the time and date on your device. Is there something else I can help you with?"
            
            # Weather questions
            if any(word in prompt_lower for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy']):
                return "I don't have access to current weather data. Try checking a weather app or website! Is there something else I can help explain?"
            
            # Conversational responses for common phrases
            if any(phrase in prompt_lower for phrase in ['how are you', 'how do you do', 'whats up']):
                return "I'm doing great, thank you for asking! I'm here and ready to help with any questions you have. What's on your mind?"
            
            if 'what is' in prompt_lower:
                # Try to extract what they're asking about
                what_topic = prompt_lower.replace('what is', '').replace('what\'s', '').strip()
                if what_topic:
                    return f"That's a great question about {what_topic}! While I don't have specific detailed information about that right now, I can help with general concepts in math, science, programming, and technology. Could you ask something more specific about {what_topic}?"
            
            if 'how to' in prompt_lower:
                return "I'd love to help you learn how to do something! I'm great with programming tutorials, math problem-solving steps, and explaining scientific processes. What specifically would you like to learn how to do?"
            
            if 'why' in prompt_lower:
                return "That sounds like a fascinating question! I enjoy explaining the 'why' behind things, especially in science, math, and technology. Could you be more specific about what you'd like to understand?"
            
            # Default response - much more engaging
            return "I'd be happy to help you! I'm particularly good at:\n• Solving math problems\n• Explaining programming concepts\n• Discussing science topics\n• Answering technology questions\n\nWhat would you like to explore together?"
            
        except Exception as e:
            return None