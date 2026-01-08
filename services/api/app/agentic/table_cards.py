from __future__ import annotations

from typing import Any, Iterable, Optional, Type

from pydantic import BaseModel


def _type_label(annotation: Any) -> str:
    # Best-effort, human friendly.
    try:
        origin = getattr(annotation, "__origin__", None)
        if origin is None:
            return getattr(annotation, "__name__", str(annotation)).replace("typing.", "")
        args = getattr(annotation, "__args__", ())
        origin_name = getattr(origin, "__name__", str(origin)).replace("typing.", "")
        if args:
            return f"{origin_name}[{', '.join(_type_label(a) for a in args)}]"
        return origin_name
    except Exception:
        return str(annotation)


def generate_table_card_markdown(
    *,
    name: str,
    model: Type[BaseModel],
    meaning: str,
    primary_key: str,
    tool_mapping: Optional[dict[str, str]] = None,
    verification: Optional[Iterable[str]] = None,
) -> str:
    tool_mapping = tool_mapping or {}
    verification = list(verification or [])

    lines: list[str] = []
    lines.append(f"# Table Card: {name}\n")
    lines.append("## Meaning")
    lines.append(meaning.strip() + "\n")
    lines.append("## Primary key")
    lines.append(f"- `{primary_key}`\n")

    lines.append("## Fields")
    for field_name, field_info in model.model_fields.items():
        ann = field_info.annotation
        typ = _type_label(ann)
        req = "required" if field_info.is_required() else "optional"
        desc = (field_info.description or "").strip()
        if desc:
            lines.append(f"- `{field_name}`: {req} {typ} — {desc}")
        else:
            lines.append(f"- `{field_name}`: {req} {typ}")
    lines.append("")

    if tool_mapping:
        lines.append("## Supported tool mapping")
        for k, v in tool_mapping.items():
            lines.append(f"- {k}: `{v}`")
        lines.append("")

    if verification:
        lines.append("## Verification (required)")
        for v in verification:
            lines.append(f"- {v}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
