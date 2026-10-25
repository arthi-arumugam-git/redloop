"""Offline attack seeds and a deliberately small search loop."""

from .base import Attacker
from .seed_attacker import SeedAttacker

__all__ = ["Attacker", "SeedAttacker"]
