"""Mock service tools; all side effects stay inside the sandbox."""

from .base import Sandbox, TOOL_SCHEMAS, inject
from . import calendar, crm, docs, gmail, github, slack, tickets, x  # Register the supported tools.

__all__ = ["Sandbox", "TOOL_SCHEMAS", "inject"]
