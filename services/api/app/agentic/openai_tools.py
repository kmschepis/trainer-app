from __future__ import annotations

from typing import Any, Dict, List


def openai_tools() -> List[Dict[str, Any]]:
    """OpenAI tool definitions (function calling).

    These names are what the LLM will call.
    The API is responsible for executing any side-effect tools.
    """

    return [
        {
            "type": "function",
            "function": {
                "name": "profile_get",
                "description": "Fetch the current user's onboarding profile.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "profile_save",
                "description": "Save the user's onboarding profile (upsert).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "profile": {
                            "type": "object",
                            "description": "Profile payload shaped like the onboarding draft.",
                        }
                    },
                    "required": ["profile"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "profile_delete",
                "description": "Delete/clear the user's onboarding profile.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "ui_action",
                "description": "Dispatch a UI action for the client UI (onboarding drawer, toast, etc). Always include action.type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "object",
                            "description": "A UI action object (A2UIAction).",
                            "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {"const": "ui.form.open"},
                                        "formId": {"const": "profile"},
                                        "draft": {"type": "object"},
                                    },
                                    "required": ["type", "formId"],
                                    "additionalProperties": False,
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {"const": "ui.form.patch"},
                                        "formId": {"const": "profile"},
                                        "patch": {"type": "object"},
                                    },
                                    "required": ["type", "formId", "patch"],
                                    "additionalProperties": False,
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {"const": "ui.form.close"},
                                        "formId": {"const": "profile"},
                                    },
                                    "required": ["type", "formId"],
                                    "additionalProperties": False,
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {"const": "ui.toast"},
                                        "message": {"type": "string"},
                                    },
                                    "required": ["type", "message"],
                                    "additionalProperties": False,
                                },
                            ],
                        }
                    },
                    "required": ["action"],
                    "additionalProperties": False,
                },
            },
        },
    ]
