from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    hint_message,
    parse_guess,
    update_score,
)


# --- check_guess: the core hint bug ---------------------------------------

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


def test_hint_direction_is_not_backwards():
    # Regression test for the original bug where "Too High" said "go HIGHER".
    assert "LOWER" in hint_message("Too High")
    assert "HIGHER" in hint_message("Too Low")


# --- parse_guess: input handling ------------------------------------------

def test_parse_valid_integer():
    assert parse_guess("42") == (True, 42, None)


def test_parse_integer_written_as_float():
    # "42.0" is a whole number, so it should be accepted as 42.
    assert parse_guess("42.0") == (True, 42, None)


def test_parse_rejects_non_whole_number():
    ok, value, _ = parse_guess("4.5")
    assert ok is False
    assert value is None


def test_parse_rejects_empty_and_non_numeric():
    assert parse_guess("")[0] is False
    assert parse_guess("   ")[0] is False
    assert parse_guess("abc")[0] is False


# --- update_score: scoring sanity -----------------------------------------

def test_wrong_guess_costs_a_consistent_penalty():
    # Both wrong outcomes should cost the same 5 points.
    assert update_score(20, "Too High", 1) == 15
    assert update_score(20, "Too Low", 1) == 15


def test_score_never_goes_negative():
    assert update_score(0, "Too Low", 3) == 0


def test_winning_sooner_scores_higher():
    # Fewer attempts -> more points.
    assert update_score(0, "Win", 1) > update_score(0, "Win", 5)
    assert update_score(0, "Win", 1) == 100


# --- get_range_for_difficulty: difficulty actually scales ------------------

def test_hard_is_wider_than_normal():
    _, easy_high = get_range_for_difficulty("Easy")
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert easy_high < normal_high < hard_high


def test_unknown_difficulty_falls_back_to_normal():
    assert get_range_for_difficulty("???") == get_range_for_difficulty("Normal")
