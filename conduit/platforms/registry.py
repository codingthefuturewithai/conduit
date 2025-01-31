from typing import Dict, Type
from conduit.platforms.base import Platform
from conduit.platforms.jira.client import JiraClient
from conduit.platforms.confluence.client import ConfluenceClient


class PlatformRegistry:
    _registry: Dict[str, Type[Platform]] = {}

    @classmethod
    def register(cls, name: str, platform_cls: Type[Platform]) -> None:
        cls._registry[name] = platform_cls

    @classmethod
    def get_platform(cls, name: str) -> Platform:
        if name not in cls._registry:
            raise ValueError(f"Platform '{name}' is not registered.")
        return cls._registry[name]()


# Register the platforms
PlatformRegistry.register("jira", JiraClient)
PlatformRegistry.register("confluence", ConfluenceClient)
