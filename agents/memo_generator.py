import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_memo(user_query, retrieved_cases):
    context = "\n\n".join([c["summary"] for c in retrieved_cases])
    prompt = f"Based on the following context and the query, draft a legal memo.\n\nContext:\n{context}\n\nQuery: {user_query}"
    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content.strip()