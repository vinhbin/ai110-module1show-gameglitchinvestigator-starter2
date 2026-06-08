"""Core game logic for the Number Guessing Game.

Refactored out of app.py so it can be unit-tested with pytest, independent
of Streamlit. All functions here are pure: same inputs -> same outputs,
no Streamlit session state involved.
"""

# Range (low, high) inclusive for each difficulty. Harder = wider range.
DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    "Hard": (1, 200),
}

# Attempts allowed per difficulty. Harder = fewer attempts.
ATTEMPT_LIMITS = {
    "Easy": 8,
    "Normal": 6,
    "Hard": 5,
}


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty.

    Unknown difficulties fall back to Normal. Hard is now genuinely the
    widest range so it is actually the hardest (the starter code had Hard
    as 1-50, narrower than Normal's 1-100).
    """
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["Normal"])


def get_attempt_limit(difficulty: str) -> int:
    """Return how many attempts are allowed for a given difficulty."""
    return ATTEMPT_LIMITS.get(difficulty, ATTEMPT_LIMITS["Normal"])


def parse_guess(raw: str):
    """Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    text = raw.strip()
    try:
        # Accept "42" and "42.0", but reject "4.5" since the game is integers.
        value = float(text)
    except ValueError:
        return False, None, "That is not a number."

    if value != int(value):
        return False, None, "Enter a whole number."

    return True, int(value), None


def check_guess(guess: int, secret: int) -> str:
    """Compare guess to secret and return the outcome as a single string.

    Returns one of: "Win", "Too High", "Too Low".

    Note: this returns ONLY the outcome string (the unit tests assert on
    this directly). The user-facing emoji hint lives in hint_message().
    """
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def hint_message(outcome: str) -> str:
    """Map an outcome to the emoji hint shown in the UI.

    "Too High" means the guess is above the secret, so the player should
    go LOWER (the starter code had this backwards).
    """
    messages = {
        "Win": "🎉 Correct!",
        "Too High": "📉 Too high — go LOWER!",
        "Too Low": "📈 Too low — go HIGHER!",
    }
    return messages.get(outcome, "")


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Update score based on outcome and attempt number.

    - Win: award more points for winning in fewer attempts (min 10).
    - Wrong guess: a small, consistent penalty, never below 0.
    """
    if outcome == "Win":
        points = max(10, 100 - 10 * (attempt_number - 1))
        return current_score + points

    # Any wrong guess ("Too High" / "Too Low") costs the same.
    return max(0, current_score - 5)
