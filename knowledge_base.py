import json
import re
import random
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class KnowledgeBase:
    def __init__(self):
        self.data = {
            "greetings": {
                "patterns": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
                "responses": [
                    "Hello! How can I help you today?",
                    "Hi there! What would you like to know?",
                    "Hey! I'm here to answer your questions.",
                    "Greetings! How may I assist you?"
                ]
            },
            "goodbye": {
                "patterns": ["bye", "goodbye", "see you", "farewell", "exit", "quit"],
                "responses": [
                    "Goodbye! Have a great day!",
                    "See you later! Feel free to come back anytime.",
                    "Bye! It was nice chatting with you.",
                    "Farewell! Take care!"
                ]
            },
            "thanks": {
                "patterns": ["thank you", "thanks", "appreciate", "grateful"],
                "responses": [
                    "You're welcome!",
                    "Happy to help!",
                    "No problem at all!",
                    "Glad I could assist you!"
                ]
            },
            "weather": {
                "patterns": ["weather", "temperature", "rain", "sunny", "cloudy", "forecast"],
                "responses": [
                    "I don't have access to real-time weather data, but I recommend checking a weather app or website for current conditions.",
                    "For accurate weather information, please check your local weather service or a weather app.",
                    "I'd love to help with weather, but I don't have current weather data. Try a weather website!"
                ]
            },
            "time": {
                "patterns": ["time", "date", "day", "hour", "minute", "clock"],
                "responses": [
                    "I don't have access to current time, but you can check the time on your device.",
                    "You can find the current time and date on your computer or phone.",
                    "I don't have real-time clock access. Please check your system time."
                ]
            },
            "programming": {
                "patterns": ["python", "code", "programming", "javascript", "html", "css", "java", "c++", "software"],
                "responses": [
                    "Programming is a great skill! What specific programming topic would you like to know about?",
                    "I can help with programming concepts! Are you interested in a particular language?",
                    "Programming questions are welcome! What would you like to learn?",
                    "There are many programming languages. What are you working on?"
                ]
            },
            "math": {
                "patterns": ["math", "mathematics", "calculate", "equation", "algebra", "geometry", "calculus"],
                "responses": [
                    "I can help with basic math concepts! What mathematical topic interests you?",
                    "Mathematics is fascinating! What specific area would you like to explore?",
                    "I'd be happy to discuss math topics. What would you like to know?",
                    "Math questions are great! What calculation or concept can I help with?"
                ]
            },
            "science": {
                "patterns": ["science", "physics", "chemistry", "biology", "astronomy", "research"],
                "responses": [
                    "Science is amazing! What scientific topic would you like to explore?",
                    "I love science questions! Which field interests you most?",
                    "Science covers so many areas. What would you like to learn about?",
                    "Scientific inquiry is wonderful! What aspect interests you?"
                ]
            },
            "help": {
                "patterns": ["help", "what can you do", "capabilities", "features", "commands"],
                "responses": [
                    "I can help answer questions on various topics like programming, math, science, and general knowledge. Just ask me anything!",
                    "I'm here to assist with information and answer your questions. Try asking me about different subjects!",
                    "I can discuss topics like technology, science, math, and more. What would you like to know?",
                    "Feel free to ask me questions about various subjects. I'll do my best to help!"
                ]
            }
        }
        
        # Initialize NLTK components
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            # If stopwords not downloaded, use basic set
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    
    def preprocess_text(self, text):
        """Clean and preprocess text for better matching"""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', '', text)
        # Tokenize
        try:
            tokens = word_tokenize(text)
        except LookupError:
            # If punkt tokenizer not available, use simple split
            tokens = text.split()
        
        # Remove stop words and lemmatize
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words:
                try:
                    lemmatized = self.lemmatizer.lemmatize(token)
                    processed_tokens.append(lemmatized)
                except:
                    processed_tokens.append(token)
        
        return ' '.join(processed_tokens)
    
    def find_best_match(self, user_input):
        """Find the best matching response category"""
        processed_input = self.preprocess_text(user_input)
        best_match = None
        best_score = 0
        
        for category, data in self.data.items():
            for pattern in data['patterns']:
                processed_pattern = self.preprocess_text(pattern)
                
                # Simple keyword matching
                if processed_pattern in processed_input or processed_input in processed_pattern:
                    score = len(processed_pattern.split())
                    if score > best_score:
                        best_score = score
                        best_match = category
                
                # Calculate similarity using basic word overlap
                input_words = set(processed_input.split())
                pattern_words = set(processed_pattern.split())
                overlap = len(input_words.intersection(pattern_words))
                if overlap > 0:
                    similarity = overlap / max(len(input_words), len(pattern_words))
                    if similarity > 0.3 and similarity * 10 > best_score:
                        best_score = similarity * 10
                        best_match = category
        
        return best_match
    
    def get_response(self, user_input):
        """Get appropriate response for user input"""
        best_match = self.find_best_match(user_input)
        
        if best_match:
            responses = self.data[best_match]['responses']
            return random.choice(responses)
        else:
            # Default responses when no match found
            default_responses = [
                "I'm not sure I understand. Could you please rephrase that?",
                "That's an interesting question! Could you provide more details?",
                "I don't have specific information about that. Can you ask something else?",
                "I'm still learning! Could you try asking in a different way?",
                "That's beyond my current knowledge. What else would you like to know?"
            ]
            return random.choice(default_responses)