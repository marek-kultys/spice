"""
Spice Recommendation Engine

Generates spice/herb recommendations for a set of food ingredients
using the pairings database extracted from The Flavor Bible.

Algorithm:
  1. Look up all known pairings for each input ingredient
  2. Assign numeric weights to pairing gradation levels
  3. Apply a multiplier for main ingredients (2x)
  4. Aggregate scores per pairing across all input ingredients
  5. Rank by breadth (number of ingredient matches), then by total score
  6. Separate out any "avoid" pairings as a no-go list
"""

import csv
import os
from collections import defaultdict

# Pairing level weights
LEVEL_WEIGHTS = {
    "holy_grail": 5,
    "very_highly_recommended": 4,
    "recommended": 3,
    "normal": 2,
}

MAIN_INGREDIENT_MULTIPLIER = 2

PAIRINGS_PATH = os.path.join(os.path.dirname(__file__), "pairings.csv")


def load_pairings(path=PAIRINGS_PATH):
    """Load the pairings database from CSV."""
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_pairings_for(ingredient_name, pairings_db):
    """Find all pairings where the ingredient column matches the given name.

    Matches the exact ingredient name or sub-entries like
    "LAMB, LEG OF" when searching for "LAMB".
    """
    name = ingredient_name.upper()
    results = []
    for row in pairings_db:
        ing = row["ingredient"].upper()
        if (
            ing == name
            or ing.startswith(name + " ")
            or ing.startswith(name + ",")
            or ing.startswith(name + " —")
        ):
            results.append(row)
    return results


def recommend(ingredients, main_ingredients=None, pairings_db=None):
    """Generate a spice recommendation for a set of food ingredients.

    Args:
        ingredients: List of ingredient names (strings).
        main_ingredients: List of ingredient names marked as main (subset of
            ingredients). These receive a scoring multiplier. Defaults to [].
        pairings_db: Pre-loaded pairings list. If None, loads from disk.

    Returns:
        dict with keys:
            "recommendations": list of dicts sorted best-first, each with:
                - "pairing": the recommended spice/herb/flavoring name
                - "score": numeric score (higher = stronger recommendation)
                - "matches": how many input ingredients this pairs with
                - "details": list of (ingredient, level) tuples
            "avoid": list of dicts, each with:
                - "pairing": the spice/herb to avoid
                - "ingredients": list of ingredient names that conflict
            "input": dict echoing back the query parameters
    """
    if pairings_db is None:
        pairings_db = load_pairings()
    if main_ingredients is None:
        main_ingredients = []

    main_set = {m.upper() for m in main_ingredients}
    all_ingredients = [i.upper() for i in ingredients]

    # Step 1: Look up pairings for each input ingredient
    ingredient_pairings = {}
    for ing in all_ingredients:
        ingredient_pairings[ing] = find_pairings_for(ing, pairings_db)

    # Steps 2-4: Score and aggregate
    scores = defaultdict(dict)  # pairing -> {ingredient: level}
    avoid = defaultdict(list)   # pairing -> [ingredient, ...]

    for ing in all_ingredients:
        for row in ingredient_pairings[ing]:
            pairing = row["pairing"]
            level = row["level"]
            if level == "avoid":
                avoid[pairing].append(ing)
            else:
                # Keep the highest level if an ingredient appears multiple times
                # (e.g. from sub-entries like LAMB and LAMB, LEG OF)
                existing = scores[pairing].get(ing)
                if existing is None or LEVEL_WEIGHTS.get(level, 0) > LEVEL_WEIGHTS.get(existing, 0):
                    scores[pairing][ing] = level

    recommendations = []
    for pairing, ing_levels in scores.items():
        total_score = 0
        details = []
        for ing, level in ing_levels.items():
            weight = LEVEL_WEIGHTS.get(level, 1)
            multiplier = MAIN_INGREDIENT_MULTIPLIER if ing in main_set else 1
            total_score += weight * multiplier
            details.append((ing, level))

        recommendations.append({
            "pairing": pairing,
            "score": total_score,
            "matches": len(ing_levels),
            "details": details,
        })

    # Step 5: Rank by breadth first, then by score
    recommendations.sort(key=lambda x: (x["matches"], x["score"]), reverse=True)

    # Step 6: Build avoid list
    avoid_list = [
        {"pairing": pairing, "ingredients": ings}
        for pairing, ings in avoid.items()
    ]

    return {
        "recommendations": recommendations,
        "avoid": avoid_list,
        "input": {
            "ingredients": all_ingredients,
            "main_ingredients": list(main_set),
        },
    }


def format_recommendation(result, top_n=15):
    """Format a recommendation result as a human-readable string."""
    lines = []
    inp = result["input"]
    ing_str = ", ".join(
        f"{i.lower()} (main)" if i in inp["main_ingredients"] else i.lower()
        for i in inp["ingredients"]
    )
    lines.append(f"Ingredients: {ing_str}")
    lines.append("")
    lines.append("--- RECOMMENDED ---")
    lines.append("")

    for rec in result["recommendations"][:top_n]:
        detail_str = ", ".join(
            f"{ing.lower()} ({lvl})" for ing, lvl in rec["details"]
        )
        star = "***" if rec["matches"] >= 3 else "**" if rec["matches"] >= 2 else " *"
        lines.append(
            f"  {star} {rec['pairing']:<35s}  "
            f"score={rec['score']:>3d}  matches={rec['matches']}  "
            f"[{detail_str}]"
        )

    if result["avoid"]:
        lines.append("")
        lines.append("--- AVOID ---")
        lines.append("")
        for a in result["avoid"]:
            ings = ", ".join(i.lower() for i in a["ingredients"])
            lines.append(f"  x  {a['pairing']:<35s}  (conflicts with: {ings})")
    else:
        lines.append("")
        lines.append("--- No spices to avoid ---")

    return "\n".join(lines)


# CLI usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python engine.py <ingredient1> <ingredient2> ... [--main <ing1> <ing2>]")
        print("Example: python engine.py lamb potatoes onions carrots --main lamb potatoes")
        sys.exit(1)

    args = sys.argv[1:]
    if "--main" in args:
        idx = args.index("--main")
        ingredients = args[:idx]
        mains = args[idx + 1:]
    else:
        ingredients = args
        mains = []

    result = recommend(ingredients, main_ingredients=mains)
    print(format_recommendation(result))
