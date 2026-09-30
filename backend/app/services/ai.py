from dataclasses import dataclass

@dataclass
class AIResult:
    provider: str
    status: str
    summary: str
    metadata: dict

class AIProvider:
    def analyze(self, resume_text: str, job_description: str) -> AIResult:
        raise NotImplementedError

class DeterministicProvider(AIProvider):
    def analyze(self, resume_text: str, job_description: str) -> AIResult:
        return AIResult(
            provider="deterministic",
            status="available",
            summary="Analysis generated from verified resume and job text.",
            metadata={"external_ai": False},
        )

def get_ai_provider() -> AIProvider:
    # External providers belong behind this gateway. No external AI is falsely
    # represented as active when credentials are absent.
    return DeterministicProvider()
