# Table Card: goals

## Meaning
User goals (many per user).

## Primary key
- `id (UUID)`

## Fields
- `type`: required Literal[body_weight, strength, conditioning, performance, other] — Goal category
- `title`: required str — Short label
- `targetDate`: optional Union[str, NoneType] — Target date (YYYY-MM-DD)
- `status`: optional Literal[active, paused, completed, canceled] — Goal status

## Verification (required)
- After any write, verify via read-back (get/list) before claiming success.
