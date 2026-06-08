# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Describe the game's purpose.** A Streamlit number-guessing game: pick a difficulty, guess the secret number within a limited number of attempts, and get "higher/lower" hints plus a score that rewards winning quickly.
- [x] **Detail which bugs you found.**
  - Hints lied on every other guess (secret was cast to a string on even attempts, breaking the comparison).
  - Hint wording was backwards ("Too High" told you to go HIGHER).
  - Scoring was incoherent — wrong guesses could *raise* the score, and it could go negative.
  - Attempt counter was off by one and an invalid input still burned an attempt.
  - "Hard" was easier than "Normal", and the range text was hard-coded to "1 and 100".
  - All logic in `logic_utils.py` was stubbed (`NotImplementedError`), so `pytest` failed immediately.
  - "New Game" didn't fully reset (old score/status/history leaked in).
- [x] **Explain what fixes you applied.** Refactored the four core functions into `logic_utils.py` so they're pure and testable; always compare against the integer secret; corrected hint wording; made scoring a consistent, non-negative penalty with a sane win bonus; fixed the attempt counter and stopped counting invalid input; made Hard genuinely the widest range with dynamic UI text; and made "New Game" reset everything. Then added pytest coverage and verified in the live app.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video:

1. User selects **Normal** difficulty (range 1–100, 6 attempts). The page shows "Attempts left: 6" before any guess.
2. User enters a guess of `40` → game returns **"📈 Too low — go HIGHER!"** and the score updates.
3. User enters a guess of `70` → game returns **"📉 Too high — go LOWER!"** (hint direction is stable, not flipping between turns).
4. After each guess "Attempts left" decreases by exactly one, and the score reflects a small, consistent penalty (never dropping below 0).
5. User enters the correct number (visible in the **Developer Debug Info** panel) → balloons appear, the game shows **"You won!"** with the secret and a final score that's higher the fewer attempts it took.
6. User clicks **New Game 🔁** → secret, attempts, score, status, and history all reset to a clean slate.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ python -m pytest tests/
============================= test session starts =============================
platform win32 -- Python 3.10.7, pytest-9.0.2, pluggy-1.6.0
collected 13 items

tests\test_game_logic.py .............                                   [100%]

============================= 13 passed in 0.07s ==============================
```

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
