from flask import Flask, request, jsonify
import os
import secrets
import string

app = Flask(__name__)

# Enforce maximum request payload size (default 16 KB) to prevent memory exhaustion DoS
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024))

SYMBOLS = os.environ.get("PASSWORD_SYMBOLS", "!@#$%^&*()_+-=[]{}|;:,.<>?")
MIN_PASSWORD_LENGTH = int(os.environ.get("MIN_PASSWORD_LENGTH", 4))
MAX_PASSWORD_LENGTH = int(os.environ.get("MAX_PASSWORD_LENGTH", 128))
_sys_random = secrets.SystemRandom()


def generate_password(
    length: int = 16,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_numbers: bool = True,
    use_symbols: bool = True,
) -> str:
    """Generate a cryptographically secure, unbiased random password."""
    if not isinstance(length, int) or isinstance(length, bool):
        raise ValueError("Password length must be an integer")

    if length < MIN_PASSWORD_LENGTH or length > MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}"
        )

    pools = []
    if use_uppercase:
        pools.append(string.ascii_uppercase)
    if use_lowercase:
        pools.append(string.ascii_lowercase)
    if use_numbers:
        pools.append(string.digits)
    if use_symbols:
        pools.append(SYMBOLS)

    if not pools:
        raise ValueError("At least one character type must be selected")

    if length < len(pools):
        raise ValueError(
            f"Password length ({length}) cannot be shorter than the number of selected character types ({len(pools)})"
        )

    # Guarantee at least one character from each enabled pool
    password_chars = [secrets.choice(pool) for pool in pools]

    # Fill the remaining length from the combined character pool
    all_characters = "".join(pools)
    password_chars.extend(
        secrets.choice(all_characters) for _ in range(length - len(pools))
    )

    # Cryptographically shuffle to eliminate positional bias
    _sys_random.shuffle(password_chars)

    return "".join(password_chars)


def evaluate_password_strength(password: str) -> dict:
    """Evaluate password strength and return score and feedback."""
    score = 0
    feedback = []
    length = len(password)

    # Check >= 12 first so it is not shadowed by >= 8
    if length >= 12:
        score += 2
        feedback.append("Excellent length")
    elif length >= 8:
        score += 1
        feedback.append("Good length")
    else:
        feedback.append("Password too short")

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in SYMBOLS for c in password)

    if has_upper:
        score += 1
        feedback.append("Has uppercase")
    if has_lower:
        score += 1
        feedback.append("Has lowercase")
    if has_digit:
        score += 1
        feedback.append("Has numbers")
    if has_symbol:
        score += 1
        feedback.append("Has symbols")

    max_score = 5
    normalized_score = min(score, max_score)

    return {
        "valid": normalized_score >= 3 and length >= 8,
        "score": normalized_score,
        "max_score": max_score,
        "feedback": feedback,
    }


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route("/api/generate", methods=["POST"])
def generate_password_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid JSON payload"}), 400

    length = data.get("length", 16)
    use_uppercase = bool(data.get("use_uppercase", True))
    use_lowercase = bool(data.get("use_lowercase", True))
    use_numbers = bool(data.get("use_numbers", True))
    use_symbols = bool(data.get("use_symbols", False))

    try:
        password = generate_password(
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_numbers=use_numbers,
            use_symbols=use_symbols,
        )
        validation = evaluate_password_strength(password)
        return jsonify(
            {
                "success": True,
                "password": password,
                "length": len(password),
                "options": {
                    "use_uppercase": use_uppercase,
                    "use_lowercase": use_lowercase,
                    "use_numbers": use_numbers,
                    "use_symbols": use_symbols,
                },
                "validation": validation,
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/validate", methods=["POST"])
def validate_password_api():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return (
            jsonify(
                {"valid": False, "score": 0, "feedback": ["Invalid JSON payload"]}
            ),
            400,
        )

    password = data.get("password", "")
    if not isinstance(password, str) or not password:
        return (
            jsonify(
                {"valid": False, "score": 0, "feedback": ["Password is required"]}
            ),
            400,
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        return (
            jsonify(
                {
                    "valid": False,
                    "score": 0,
                    "feedback": [
                        f"Password exceeds maximum length of {MAX_PASSWORD_LENGTH}"
                    ],
                }
            ),
            400,
        )

    return jsonify(evaluate_password_strength(password))


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5001))
    app.run(host=host, port=port, debug=debug_mode)
