from backend.app.agents.orchestrator_agent import OrchestratorAgent

_orchestrator_instance = None

def get_orchestrator() -> OrchestratorAgent:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OrchestratorAgent()
    return _orchestrator_instance
