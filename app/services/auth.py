"""
Authentication and security utilities
"""
import bcrypt
import secrets


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_reset_token() -> str:
    """Generate a secure token for password reset"""
    return secrets.token_urlsafe(32)


def send_reset_email(email: str, token: str):
    """Simulate sending password reset email"""
    reset_link = f"http://127.0.0.1:5500/static/index.html?token={token}"
    print(f"\n{'='*60}")
    print(f"PASSWORD RESET EMAIL")
    print(f"To: {email}")
    print(f"Reset Link: {reset_link}")
    print(f"Token: {token}")
    print(f"{'='*60}\n")
    print(f"\n🔗 COPY THIS LINK:")
    print(f"{reset_link}")
    print(f"{'='*60}\n")
    # In production, use SMTP for real email sending

