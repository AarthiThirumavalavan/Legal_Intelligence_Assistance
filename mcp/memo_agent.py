# mcp/memo_agent.py - IMPROVED VERSION
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

class MemoAgent:
    def process(self, context):
        if context.intent == "memo_generation":
            # Generate full legal memo
            context_text = "\n\n".join([c["summary"] for c in context.retrieved_cases])
            prompt = f"Based on the following context and the query, draft a legal memo.\n\nContext:\n{context_text}\n\nQuery: {context.user_query}"
            res = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            context.memo = res.choices[0].message.content.strip()
            context.log("Full legal memo generated")
            
        elif context.intent == "precedent_lookup" and context.retrieved_cases:
            # Generate case summary instead of full memo
            case_summaries = []
            for case in context.retrieved_cases:
                case_summaries.append(f"**{case.get('title', 'Unknown')}** ({case.get('case_id', 'N/A')}): {case.get('summary', 'No summary available')}")
            
            context.memo = f"**Retrieved Cases for: {context.user_query}**\n\n" + "\n\n".join(case_summaries)
            context.log("Case summaries compiled")
            
        elif context.intent == "faq":
            # Generate FAQ-style response
            prompt = f"Answer this legal question in a clear, FAQ-style format: {context.user_query}"
            res = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            context.memo = res.choices[0].message.content.strip()
            context.log("FAQ response generated")
            
        else:
            context.memo = "No memo generated for this intent."
            context.log("Memo agent skipped")
            
        return context