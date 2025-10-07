import os
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path


class TalksConfig:
    """Singleton configuration class for AI Talks"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from talks.yml file"""
        # Look for config file in project root
        config_paths = [
            Path("talks.yml"),
            Path(__file__).parent.parent.parent / "talks.yml",
            Path.cwd() / "talks.yml"
        ]
        
        config_file = None
        for path in config_paths:
            if path.exists():
                config_file = path
                break
        
        if not config_file:
            # Use default configuration if no file found
            self._config = self._get_default_config()
            return
        
        try:
            with open(config_file, 'r') as f:
                self._config = yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_file}: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "forbidden_topics": ["pop culture references"],
            "narrator": {
                "default_name": "Michael Lee",
                "enabled": True
            },
            "discussion": {
                "default_depth": 3,
                "max_turns": 30,
                "min_participants": 2,
                "max_participants": 5
            },
            "personality_types": [
                "analytical", "collaborative", "assertive",
                "cautious", "creative", "skeptical"
            ],
            "expertise_areas": [
                "ethics", "logic", "science", "philosophy",
                "psychology", "mathematics", "history", "literature"
            ]
        }
    
    @property
    def forbidden_topics(self) -> List[str]:
        """Get list of forbidden topics"""
        return self._config.get("forbidden_topics", ["pop culture references"])
    
    @property
    def narrator_name(self) -> str:
        """Get default narrator name"""
        return self._config.get("narrator", {}).get("default_name", "Michael Lee")
    
    @property
    def narrator_enabled(self) -> bool:
        """Check if narrator is enabled by default"""
        return self._config.get("narrator", {}).get("enabled", True)
    
    @property
    def coordinator_mode(self) -> bool:
        """Check if coordinator mode is enabled"""
        return self._config.get("narrator", {}).get("coordinator_mode", False)
    
    @property
    def coordinator_frequency(self) -> int:
        """Get coordinator interjection frequency (every N turns)"""
        return self._config.get("narrator", {}).get("coordinator_frequency", 3)
    
    @property
    def default_depth(self) -> int:
        """Get default discussion depth"""
        return self._config.get("discussion", {}).get("default_depth", 3)
    
    @property
    def max_turns(self) -> int:
        """Get maximum number of turns"""
        return self._config.get("discussion", {}).get("max_turns", 30)
    
    @property
    def recursion_limit(self) -> int:
        """Get recursion limit for LangGraph"""
        return self._config.get("discussion", {}).get("recursion_limit", 250)
    
    @property
    def personality_types(self) -> List[str]:
        """Get available personality types"""
        return self._config.get("personality_types", [
            "analytical", "collaborative", "assertive",
            "cautious", "creative", "skeptical"
        ])
    
    @property
    def expertise_areas(self) -> List[str]:
        """Get available expertise areas"""
        return self._config.get("expertise_areas", [
            "ethics", "logic", "science", "philosophy",
            "psychology", "mathematics", "history", "literature"
        ])
    
    def reload(self):
        """Reload configuration from file"""
        self._load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys with dots)"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value