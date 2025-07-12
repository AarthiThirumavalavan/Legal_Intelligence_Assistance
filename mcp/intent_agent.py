# mcp/intent_agent.py - FIXED VERSION
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

class IntentAgent:
    def process(self, context):
        prompt = f"""Classify the intent of this legal query: '{context.user_query}'. 
        
        Return ONLY ONE of these exact words:
        - precedent_lookup
        - memo_generation  
        - faq
        
        Do not include any explanation or additional text."""
        
        res = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )
        
        intent_response = res.choices[0].message.content.strip()
        
        # Extract just the intent keyword
        if "precedent_lookup" in intent_response.lower():
            context.intent = "precedent_lookup"
        elif "memo_generation" in intent_response.lower():
            context.intent = "memo_generation"
        elif "faq" in intent_response.lower():
            context.intent = "faq"
        else:
            context.intent = "precedent_lookup"  # Default fallback
            
        context.log(f"Intent detected: {context.intent}")
        return context