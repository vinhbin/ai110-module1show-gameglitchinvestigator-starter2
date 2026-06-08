# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the game it *looked* fine — it loaded in Streamlit with a difficulty selector, a guess box, and a "Developer Debug Info" panel that revealed the secret number. But playing it was maddening. Even when I read the secret straight from the debug panel and typed it in, the hints often pointed me the wrong way, and on alternating guesses the game seemed to "change its mind" about whether I was high or low. My score also bounced around in ways that made no sense — sometimes a wrong guess *raised* it.

Concrete bugs I noticed at the start:

- **The hints lie on every other guess.** The secret is silently converted to a *string* on even-numbered attempts ([`app.py:158-161`](app.py#L158-L161)), so `check_guess` compares an `int` to a `str`, falls into a `TypeError` fallback that compares text lexicographically, and returns a bogus "Higher/Lower". That's the "secret has commitment issues" symptom from the README.
- **The hint wording is backwards.** Even when the comparison works, "Too High" tells you to *"Go HIGHER!"* and "Too Low" tells you to *"Go LOWER!"* ([`app.py:38`](app.py#L38), [`app.py:46`](app.py#L46)) — the opposite of what should happen.
- **The score is incoherent.** `update_score` ([`app.py:50-65`](app.py#L50-L65)) *subtracts* points for "Too Low", randomly adds or subtracts for "Too High" based on whether the attempt number is even, and the win bonus is off by one (`attempt_number + 1`). The score can go negative.
- **The attempt counter is off by one** — `attempts` starts at `1` ([`app.py:96`](app.py#L96)) so "Attempts left" is already wrong on the first turn, and "New Game" resets it to `0` instead ([`app.py:135`](app.py#L135)), so the two paths disagree.
- **"Hard" is easier than "Normal"** — Hard's range is `1–50` while Normal's is `1–100` ([`app.py:9-10`](app.py#L9-L10)), and the prompt text is hard-coded to "between 1 and 100" regardless of difficulty ([`app.py:110`](app.py#L110)).
- **The logic isn't testable.** Every function in [`logic_utils.py`](logic_utils.py) just `raise NotImplementedError`, and the starter tests import `check_guess` from it, so `pytest` fails before running a single real assertion.
- **"New Game" doesn't fully reset** — it only resets the secret and attempts, leaving the old score, status, and history in place ([`app.py:134-138`](app.py#L134-L138)).

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Secret = 50 (from debug panel), guess `60` on an **even** attempt | Hint "Too High" → "Go LOWER!" | Lexicographic string compare (`"60" > "50"`) gives a misleading hint; behavior flips between attempts | none (silent `TypeError` swallowed by the `except` branch in `check_guess`) |
| Secret = 50, guess `60` on an **odd** attempt | "Go LOWER!" | Hint reads **"📈 Go HIGHER!"** (wording reversed) | none |
| Two wrong "Too Low" guesses in a row from score 0 | Score stays ≥ 0 / penalty is consistent | Score drops to `-10`; a later "Too High" on an even attempt *adds* 5 | none |
| Fresh game, before guessing | "Attempts left: 8" (Normal) | Shows "Attempts left: 7" because `attempts` starts at 1 | none |
| Select **Hard**, read range | Hard range narrower/harder than Normal; UI shows correct bounds | Range is `1–50` (easier than Normal) and UI still says "between 1 and 100" | none |
| Run `pytest` on starter code | Tests run against real logic | All 3 tests error out immediately | `NotImplementedError: Refactor this function from app.py into logic_utils.py` (`logic_utils.py:21`) |

---

## 2. How did you use AI as a teammate?

I used an AI coding assistant (Claude in VS Code, agent mode) as a pair programmer. I drove the investigation — I read the code, decided which bugs to chase, and marked the "crime scenes" — and used the AI to explain confusing lines, propose fixes, and generate pytest cases that I then reviewed.

**A correct, helpful suggestion.** When I asked why the hints flipped on every other guess, the AI traced it to [`app.py:158-161`](app.py#L158-L161), where the secret is cast to `str` on even attempts so `check_guess` ends up comparing an `int` to a `str` and silently falls into a `TypeError` branch doing lexicographic comparison. It suggested deleting that cast and always comparing against the integer secret. I verified this by adding `test_guess_too_high`/`test_guess_too_low` (which now pass) and by playing the game with the debug panel open — the hint direction is now stable across consecutive guesses.

**A misleading suggestion I rejected/modified.** At first the assistant wanted `check_guess` to keep returning a `(outcome, message)` tuple "so the UI still has its emoji string." That sounded reasonable, but the provided tests assert `check_guess(50, 50) == "Win"` — a *string*, not a tuple — so following that advice would have left the starter tests failing. I rejected it and instead had `check_guess` return only the outcome string and split the emoji text into a separate `hint_message()` helper. I verified the choice by running `pytest`: all three original tests pass against the single-string contract. This was a good reminder that the AI doesn't automatically know the existing test contract — I had to hold it to that.

---

## 3. Debugging and testing your fixes

I decided a bug was "really fixed" only when I had both a green automated test *and* the matching behavior in the live game — one without the other wasn't enough. For example, after fixing the scoring logic I added `test_score_never_goes_negative` and `test_wrong_guess_costs_a_consistent_penalty`; running `python -m pytest tests/ -v` showed all 13 tests passing, which told me `update_score` no longer rewards wrong guesses or drops below zero. I also re-ran the app with `streamlit run app.py` and watched the score and "Attempts left" counter behave sanely from the first guess.

AI helped me design the tests by drafting the initial pytest cases, but I reviewed and tightened each one — I added a regression test (`test_hint_direction_is_not_backwards`) specifically aimed at the original "backwards hint" bug, and a `test_hard_is_wider_than_normal` to lock in the difficulty fix, so the same glitches can't silently come back.

---

## 4. What did you learn about Streamlit and state?

I'd explain it like this: every time you interact with a Streamlit app — click a button, type in a box — Streamlit doesn't update just that one piece. It re-runs your *entire* Python script from the top, like reloading the page. That means any normal variable you create gets thrown away and recalculated on every interaction. So if you wrote `secret = random.randint(1, 100)` as a plain variable, you'd get a *new* secret on every click, which is exactly one of the bugs here. `st.session_state` is the fix: it's a little dictionary that *survives* between reruns, so values you store there (the secret, the score, the attempt count) persist instead of resetting. The mental model that made it click for me: the script runs top-to-bottom every time, and `session_state` is the only memory that carries over.

---

## 5. Looking ahead: your developer habits

- **One habit I want to reuse:** writing a regression test the moment I fix a bug, named after the bug itself (e.g. `test_hint_direction_is_not_backwards`). It turns "I think I fixed it" into "the suite proves it's fixed and will catch it if it comes back," and it forced me to actually understand the bug well enough to assert on it.
- **One thing I'd do differently with AI:** give it the constraints *up front* instead of after it guesses wrong. The AI initially proposed a return type that broke the existing tests because I hadn't told it the test contract first. Next time I'll attach the tests and say "your change must keep these green" before asking for the fix.
- **How this changed how I think about AI-generated code:** I now treat AI output as a confident first draft from a teammate who hasn't read all the requirements — useful and fast, but something I have to verify against tests and the running app before I trust it. The AI is great at proposing; the judgment about whether a proposal is actually correct still has to be mine.
