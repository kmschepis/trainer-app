# Table Card: notes

## Meaning
Coach notes (many per user), stored as markdown.

## Primary key
- `id (UUID)`

## Fields
- `type`: required Literal[restriction, preference, equipment, injury, general] — Note category
- `title`: optional Union[str, NoneType] — Optional title
- `bodyMd`: required str — Markdown content

## Verification (required)
- After any write, verify via read-back (get/list) before claiming success.
