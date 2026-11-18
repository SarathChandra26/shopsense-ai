import json
import httpx
from typing import Optional, Dict, Any, List
from backend.app.core.config import settings
from backend.app.core.logging import logger

class OllamaClient:
    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model: str = settings.OLLAMA_MODEL,
        timeout: int = settings.OLLAMA_TIMEOUT_SECONDS
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if local Ollama daemon is active and responding."""
        try:
            with httpx.Client(timeout=0.3) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def list_local_models(self) -> List[str]:
        """List downloaded models in local Ollama instance."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.2
    ) -> Optional[str]:
        """Send chat completion to local Ollama instance."""
        if not self.is_available():
            return None

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "options": {
                "temperature": temperature,
            },
            "stream": False
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    msg = data.get("message", {}).get("content", "")
                    return msg.strip()
        except Exception as e:
            logger.warning(f"Ollama chat completion call failed: {e}")
        return None
