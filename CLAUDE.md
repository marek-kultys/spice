# Spice — CLAUDE.md

## What this project is

Spice is a personal flavour-pairing tool. The user inputs food ingredients and gets back a ranked list of recommended spices/herbs to use, plus a no-go list of flavours to avoid. The pairing data comes from *The Flavor Bible* and is stored in `pairings.csv`.

## Current task: MVP web app for personal value testing

Build a minimal static web app so the owner can add it to their iPhone home screen and test the core value proposition in the kitchen over several weeks.

**Deployment target:** GitHub Pages. Output must be a single self-contained `index.html` (with inline or adjacent CSS/JS — no build step, no bundler, no framework). It must work offline once loaded.

## MVP scope — build only these two screens

### Screen 1: Ingredient input

- A text input where the user types an ingredient name
- As they type, show a dropdown of matching suggestions sourced from `vocabulary.json` (the controlled vocabulary)
- User selects an ingredient from the dropdown (free-text entry is not allowed — must match vocabulary)
- Selected ingredients appear as removable chips/tags below the input
- Up to 5 ingredients can be added
- Each ingredient chip has a toggle to mark it as "main" (up to 2 can be marked main)
- A "Get pairings" button submits the query and transitions to Screen 2

### Screen 2: Recommendation view

- Shows the list of input ingredients (with "main" labelled)
- Shows a ranked list of recommended flavour pairings, each with a strength label. Derive the label from the highest pairing level found across all matched ingredients for that pairing: `holy_grail` → "Holy grail", `very_highly_recommended` → "Very highly recommended", `recommended` → "Recommended", `normal` → "Normal". Do not try to derive the label from the computed score.
- Shows the no-go list of flavours to avoid
- A "Start over" button returns to Screen 1 (clears state)

No persistence of any kind — no saved history, no favourites, no preferences. Every session starts fresh.

## Recommendation engine

Port the logic from `engine.py` to JavaScript. The algorithm is:

1. Load `pairings.csv` (convert to JSON at build time or fetch at runtime — see note below)
2. For each input ingredient, find all rows where the `ingredient` column matches (exact or prefix match on uppercase, e.g. "LAMB" matches "LAMB, LEG OF")
3. Weight pairing levels: `holy_grail=5`, `very_highly_recommended=4`, `recommended=3`, `normal=2`, `avoid` → no-go list
4. Apply 2× multiplier to scores for main ingredients
5. Aggregate scores across all ingredients; rank by number of matching ingredients first, then by total score
6. Return top 15 recommendations and the avoid list

**Vocabulary file:** `vocabulary.json` contains a single key `"ingredients"` whose value is a flat array of strings (e.g. `"Avocados"`, `"Lamb"`). Use this array as the autocomplete source. Match case-insensitively against what the user types.

**Data file:** `pairings.csv` is 22,000+ rows. Convert it to a JSON array at the start of implementation (can be done with a small script or inline in the build) and load it with `fetch()` from a `pairings.json` file sitting next to `index.html`. The `pairings.json` file is currently empty — regenerate it from `pairings.csv`.

## What NOT to build

Do not implement any of the following (full product features, not MVP):

- Saved recommendations history
- Favourites
- Personal preferences / dietary requirements
- Filtering or search of past results
- User accounts or any backend
- Any cloud connectivity

## File structure

Keep it simple:

```
index.html        ← the entire app
pairings.json     ← generated from pairings.csv
vocabulary.json   ← already exists, use as-is
```

## Style

Mobile-first. Clean, minimal. Should feel usable one-handed in a kitchen. No external CSS frameworks — keep the stylesheet small and inline or in a `<style>` block. Use system fonts.
