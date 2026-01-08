# Table Card: profiles

## Meaning
User onboarding profile (demographic/contact + basic training context). One-to-one with users.

## Primary key
- `user_id (UUID, unique)`

## Fields
- `firstName`: optional str — Given name
- `lastName`: optional str — Family name
- `email`: optional str — Email address
- `phone`: optional str — Phone number
- `goals`: optional str — High level training goals
- `experience`: optional str — Training experience level
- `constraints`: optional str — Schedule/time constraints
- `equipment`: optional str — Equipment access
- `injuriesOrRiskFlags`: optional str — Injuries and risk flags
- `dietPrefs`: optional str — Diet preferences
- `metrics`: optional ForwardRef("'ProfileMetrics'")

## Supported tool mapping
- Get: `profile_get({})`
- Upsert: `profile_save({ profile: { ... } })`
- Delete: `profile_delete({})`

## Verification (required)
- After any write, verify via read-back (get/list) before claiming success.
