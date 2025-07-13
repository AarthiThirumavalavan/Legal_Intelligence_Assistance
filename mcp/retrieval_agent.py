# mcp/retrieval_agent.py - FIXED VERSION
from db.embed import retrieve_similar_cases

class RetrievalAgent:
    def process(self, context):
        # print(f"DEBUG: Intent received: '{context.intent}'")  # Debug line
        # print(f"DEBUG: Intent type: {type(context.intent)}")  # Debug line
        
        # The issue might be that the intent contains extra text
        # Let's check if the intent CONTAINS the keywords instead of exact match
        intent_lower = context.intent.lower() if context.intent else ""
        
        if ("precedent_lookup" in intent_lower or 
            "memo_generation" in intent_lower or
            "precedent" in intent_lower or
            "lookup" in intent_lower):
            try:
                context.retrieved_cases = retrieve_similar_cases(context.user_query)
                context.log(f"Retrieved {len(context.retrieved_cases)} cases")
                print(f"Successfully retrieved {len(context.retrieved_cases)} cases")
            except Exception as e:
                print(f"Error retrieving cases: {e}")
                context.retrieved_cases = []
                context.log(f"Error retrieving cases: {e}")
        else:
            context.retrieved_cases = []
            context.log("No case retrieval needed for this intent")
            print(f"No retrieval - intent was: '{context.intent}'")
        
        return context