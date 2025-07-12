# mcp/context.py
class MCPContext:
    def __init__(self, user_query):
        self.user_query = user_query
        self.intent = None
        self.retrieved_cases = []
        self.memo = None
        self.logs = []
    
    def log(self, message):
        self.logs.append(message)
