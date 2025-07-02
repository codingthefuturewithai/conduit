from typing import Dict, Optional, Type

from conduit.platforms.base import Platform
from conduit.platforms.confluence.client import ConfluenceClient
from conduit.platforms.jira.client import JiraClient


class PlatformRegistry:
    _registry: Dict[str, Type[Platform]] = {}

    @classmethod
    def register(cls, name: str, platform_cls: Type[Platform]) -> None:
        cls._registry[name] = platform_cls

    @classmethod
    def get_platform(cls, name: str, site_alias: Optional[str] = None) -> Platform:
        if name not in cls._registry:
            raise ValueError(f"Platform '{name}' is not registered.")
        platform_cls = cls._registry[name]
        if name in ["jira", "confluence"]:
            return platform_cls(site_alias=site_alias)
        return platform_cls()


# Register the platforms
PlatformRegistry.register("jira", JiraClient)
PlatformRegistry.register("confluence", ConfluenceClient)
