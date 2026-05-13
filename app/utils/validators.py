def validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError("password_too_short")
    if not any(c.isupper() for c in v):
        raise ValueError("password_no_uppercase")
    if not any(c.isdigit() for c in v):
        raise ValueError("password_no_digit")
    return v