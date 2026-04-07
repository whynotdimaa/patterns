"""
Builder Pattern — ConnectionBuilder.
Покроково будує конфігурацію підключення до бази даних.
"""

from __future__ import annotations
from typing import Any


class ConnectionConfig:
    """Незмінний об'єкт конфігурації підключення."""

    def __init__(self, data: dict[str, Any]):
        self._data = dict(data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __repr__(self) -> str:
        safe = {k: ("***" if "password" in k.lower() else v)
                for k, v in self._data.items()}
        return f"ConnectionConfig({safe})"


class ConnectionBuilder:
    """
    Builder для створення ConnectionConfig.
    Підтримує ланцюжок викликів (fluent interface).
    """

    def __init__(self) -> None:
        self._cfg: dict[str, Any] = {}

    def set_type(self, db_type: str) -> "ConnectionBuilder":
        self._cfg["type"] = db_type.lower()
        return self

    def set_host(self, host: str) -> "ConnectionBuilder":
        self._cfg["host"] = host
        return self

    def set_port(self, port: int) -> "ConnectionBuilder":
        self._cfg["port"] = port
        return self

    def set_database(self, db: str) -> "ConnectionBuilder":
        self._cfg["database"] = db
        return self

    def set_credentials(self, user: str, password: str) -> "ConnectionBuilder":
        self._cfg["user"] = user
        self._cfg["password"] = password
        return self

    def set_option(self, key: str, value: Any) -> "ConnectionBuilder":
        self._cfg[key] = value
        return self

    def build(self) -> ConnectionConfig:
        if "type" not in self._cfg:
            raise ValueError("Тип підключення є обов'язковим (викличте set_type())")
        return ConnectionConfig(self._cfg)
