"""Centralized test-data generation for API and UI tests.

Uses Faker for realistic values with deterministic seeding for reproducibility.
Callers may override any generated field via keyword arguments.

Key principle: all generators that need uniqueness per session use
``_fake.unique.xxx()``.  With a fixed seed the *sequence* is deterministic
(CI → CI reproducible), but the ``.unique`` proxy guarantees no duplicate
value within a single run.
"""

from __future__ import annotations

import secrets
import string
from typing import Any

from faker import Faker

_fake = Faker()

# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

_SEED: int | None = None


def set_seed(seed: int = 0) -> None:
    """Set a deterministic Faker seed (called once in pytest_configure).

    Same seed + same call order = same sequence of values across runs.
    """
    global _SEED
    _SEED = seed
    Faker.seed(seed)


def get_seed() -> int | None:
    return _SEED


# ---------------------------------------------------------------------------
# Public factories
# ---------------------------------------------------------------------------


def generate_unique_email(
    prefix: str = "test",
    domain: str = "e2e.example",
) -> str:
    """Generate a unique but realistic test email address.

    Args:
        prefix: Fixed leading segment (e.g. ``"reg"``, ``"totp"``).
        domain: Domain part; override for alternative providers.
    """
    token = _fake.unique.lexify(text="?" * 8).lower()
    return f"{prefix}-{token}@{domain}"


def generate_unique_slug(prefix: str = "e2e") -> str:
    """Generate a unique URL slug for entity creation (Brand, Category, …).

    Uses a real dictionary word so slugs read naturally:
    ``e2e-cat-forest`` instead of ``e2e-cat-a1b2c3d4``.

    Args:
        prefix: Leading segment, e.g. ``"e2e-cat"``, ``"e2e-brand"``.
    """
    word = _fake.unique.word().lower().replace(" ", "-")[:12]
    return f"{prefix}-{word}"


def generate_unique_product_name(prefix: str = "E2E Product") -> str:
    """Generate a human-readable product name for test entities.

    Args:
        prefix: Typically ``"E2E Product"`` to tag test-created products.
    """
    adjective = _fake.word().capitalize()
    noun = _fake.word().capitalize()
    return f"{prefix} {adjective} {noun}"


def generate_valid_password(length: int = 16) -> str:
    """Generate a password that satisfies the Toolshop policy.

    Guarantees: ≥8 chars, ≥1 uppercase, ≥1 lowercase, ≥1 digit, ≥1 special.

    Uses ``secrets`` (cryptographic randomness) rather than Faker, because
    passwords are security-relevant.
    """
    assert length >= 8, "password too short"

    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*")

    pool = string.ascii_letters + string.digits + "!@#$%^&*"
    filler = [secrets.choice(pool) for _ in range(length - 4)]

    chars = [upper, lower, digit, special] + filler
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def new_user_data(**overrides: Any) -> dict[str, Any]:
    """Return a complete user-registration payload with realistic defaults.

    All top-level keys may be overridden via keyword arguments.
    Address fields are nested — use flat keys with ``address_`` prefix:

    - ``address_street`` → ``address["street"]``
    - ``address_city``
    - ``address_state``
    - ``address_country``
    - ``address_postal_code``

    Example::

        data = new_user_data(
            email=existing_user["email"],
            password="Simple1!",
            address_city="Berlin",
        )
    """
    # Pull out nested address overrides
    address_overrides: dict[str, Any] = {}
    for flat_key in (
        "address_street",
        "address_city",
        "address_state",
        "address_country",
        "address_postal_code",
    ):
        if flat_key in overrides:
            nested = flat_key.replace("address_", "")
            address_overrides[nested] = overrides.pop(flat_key)

    data: dict[str, Any] = {
        "first_name": _fake.first_name(),
        "last_name": _fake.last_name(),
        "email": generate_unique_email(),
        "password": generate_valid_password(),
        "address": {
            "street": _fake.street_name(),
            "city": _fake.city(),
            "state": _fake.state(),
            "country": "DE",
            "postal_code": _fake.postcode(),
            **address_overrides,
        },
        "dob": "1990-01-01",
    }
    data.update(overrides)
    return data


def unique_id(length: int = 8) -> str:
    """Public unique token for callers needing raw custom assembly.

    Returns ``length`` lowercase letters.  Uses ``.unique`` so the same
    token never appears twice in a session.
    """
    return _fake.unique.lexify(text="?" * length).lower()
