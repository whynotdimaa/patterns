"""
Singleton Pattern — ConnectionRegistry.
Єдиний глобальний реєстр конфігурацій підключень до баз даних.
"""

from __future__ import annotations
from threading import Lock
from typing import Any


# class ConnectionRegistry:
#     """
#     Singleton-реєстр конфігурацій підключень.
#     Потокобезпечна реалізація через Lock.
#     """
#
#     _instance: "ConnectionRegistry | None" = None
#     _lock: Lock = Lock()
#
#     def __new__(cls) -> "ConnectionRegistry":
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super().__new__(cls)
#                 cls._instance._configs: dict[str, dict] = {}
#         return cls._instance
#
#     def register(self, name: str, config: dict[str, Any]) -> None:
#         """Реєструє нову конфігурацію підключення."""
#         self._configs[name] = config
#         print(f"[Registry] Зареєстровано підключення: {name!r} (тип={config.get('type')})")
#
#     def get(self, name: str) -> dict[str, Any]:
#         if name not in self._configs:
#             raise KeyError(f"Підключення {name!r} не знайдено в реєстрі")
#         return self._configs[name]
#
#     def all_names(self) -> list[str]:
#         return list(self._configs.keys())
#
#     def __repr__(self) -> str:
#         return f"ConnectionRegistry(connections={self.all_names()})"


class _RegistryMeta(type):
    """
    Метаклас, що реалізує Singleton через __call__,
    не засмічуючи простір імен цільового класу.
    """
    __slots__ = ("_instance", "_lock")

    def __init__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        cls._instance: "ConnectionRegistry | None" = None
        cls._lock: Lock = Lock()

    def __call__(cls) -> "ConnectionRegistry":  # type: ignore[override]
        # Перша перевірка — без Lock (fast path для вже створеного екземпляра)
        if cls._instance is None:
            with cls._lock:
                # Друга перевірка — всередині Lock (safe path)
                if cls._instance is None:
                    obj = cls.__new__(cls)
                    obj._configs = {}  # ініціалізуємо тут, не в __init__
                    cls._instance = obj
        return cls._instance


class ConnectionRegistry(metaclass=_RegistryMeta):
    """
    Singleton-реєстр конфігурацій підключень.

    Порівняно з базовою версією:
      - Немає __dict__ (економія ~56 байт/об'єкт завдяки __slots__)
      - Lock захоплюється лише при першому створенні (double-checked locking)
      - Без зайвих deepcopy — ConnectionConfig вже незмінний
    """
    __slots__ = ("_configs",)

    def register(self, name: str, config: Any) -> None:
        """Реєструє конфігурацію підключення за іменем."""
        self._configs[name] = config
        print(f"[Registry] Зареєстровано: {name!r}  (тип={config.get('type')})")

    def get(self, name: str) -> Any:
        try:
            return self._configs[name]
        except KeyError:
            raise KeyError(f"Підключення {name!r} не знайдено в реєстрі") from None

    def all_names(self) -> list[str]:
        return list(self._configs)

    def __repr__(self) -> str:
        return f"ConnectionRegistry(connections={self.all_names()})"