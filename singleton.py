"""
Singleton Pattern — ConnectionRegistry.
Єдиний глобальний реєстр конфігурацій підключень до баз даних.
"""

from __future__ import annotations
from threading import Lock
from typing import Any


class ConnectionRegistry:
    """
    Singleton-реєстр конфігурацій підключень.
    Потокобезпечна реалізація через Lock.
    """

    _instance: "ConnectionRegistry | None" = None
    _lock: Lock = Lock()

    def __new__(cls) -> "ConnectionRegistry":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._configs: dict[str, dict] = {}
        return cls._instance

    def register(self, name: str, config: dict[str, Any]) -> None:
        """Реєструє нову конфігурацію підключення."""
        self._configs[name] = config
        print(f"[Registry] Зареєстровано підключення: {name!r} (тип={config.get('type')})")

    def get(self, name: str) -> dict[str, Any]:
        if name not in self._configs:
            raise KeyError(f"Підключення {name!r} не знайдено в реєстрі")
        return self._configs[name]

    def all_names(self) -> list[str]:
        return list(self._configs.keys())

    def __repr__(self) -> str:
        return f"ConnectionRegistry(connections={self.all_names()})"
