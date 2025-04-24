from __future__ import annotations

import secrets
import string


def generate_password(length: int = 16) -> str:
    """Generate a secure password with letters, digits, and special characters.

    Args:
    ----
        length (int): The length of the password to generate. Defaults to 16.

    Returns:
    -------
        str: A secure password of the specified length.

    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def generate_django_secret_key(length: int = 50) -> str:
    """Generate a Django SECRET_KEY.

    Args:
    ----
        length (int): The length of the secret key to generate. Defaults to 50.

    Returns:
    -------
        str: A Django SECRET_KEY of the specified length.

    """
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

def generate_credentials() -> dict[str, str]:
    """Generate secure credentials for environment variables.

    Returns
    -------
        dict[str, str]: A dictionary of environment variables with secure values.

    """
    return {
        "POSTGRESQL_PASSWORD": generate_password(20),
        "RABBITMQ_DEFAULT_PASS": generate_password(20),
        "DJANGO_SECRET_KEY": generate_django_secret_key(),
        "DJANGO_ADMIN_PASSWORD": generate_password(20),
        "REDIS_PASSWORD": generate_password(20),
    }

# Example Usage
if __name__ == "__main__":
    credentials = generate_credentials()
    for key, value in credentials.items():
        print(f"{key}: {value}")  # noqa: T201
