# mcp/orchestrator.py
class Orchestrator:
    def __init__(self, agents):
        self.agents = agents
    
    def run(self, context):
        for agent in self.agents:
            context = agent.process(context)
        return context
