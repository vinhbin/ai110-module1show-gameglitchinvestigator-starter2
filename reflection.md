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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
