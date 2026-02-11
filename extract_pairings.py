#!/usr/bin/env python3
"""Extract food-spice pairings from The Flavor Bible PDF using font detection."""

import pdfplumber
import csv
import re
import sys

PDF_PATH = "/Users/marekkultys/Git Repos/spice/Flavor-Bible-epub.pdf"


def extract_lines_with_font_info(pdf, start_page, end_page):
    """Extract lines with bold/regular font info from a range of pages."""
    all_lines = []

    for page_num in range(start_page, end_page):
        if page_num >= len(pdf.pages):
            break
        page = pdf.pages[page_num]
        chars = page.chars
        if not chars:
            continue

        # Group chars into lines by y-position (top coordinate)
        lines_by_y = {}
        for c in chars:
            y_key = round(c['top'], 0)
            if y_key not in lines_by_y:
                lines_by_y[y_key] = []
            lines_by_y[y_key].append(c)

        for y_key in sorted(lines_by_y.keys()):
            line_chars = sorted(lines_by_y[y_key], key=lambda c: c['x0'])

            # Build text with proper spacing (collapse tabs to spaces)
            raw_text = ''.join(c['text'] for c in line_chars).strip()
            # Replace tab characters with single space
            text = re.sub(r'\t+', ' ', raw_text)
            text = re.sub(r'  +', ' ', text)
            if not text:
                continue

            # Determine if line is bold: check if the FIRST substantive word is bold
            # This handles cases like "PESTO (key ingredient)" where PESTO is bold
            # but "(key ingredient)" is not
            first_alpha_chars = [c for c in line_chars if c['text'].strip() and c['text'].isalpha()]
            if first_alpha_chars:
                # Check the first few alpha characters
                first_chars = first_alpha_chars[:3]
                is_bold = any('Bold' in c.get('fontname', '') for c in first_chars)
            else:
                is_bold = False

            # Check font size to detect headers
            sizes = [c['size'] for c in line_chars if c['text'].strip()]
            avg_size = sum(sizes) / len(sizes) if sizes else 0

            all_lines.append({
                'text': text,
                'is_bold': is_bold,
                'avg_size': avg_size,
                'page': page_num + 1,  # 1-indexed
            })

    return all_lines


def classify_pairing(text, is_bold):
    """Classify a pairing line into its gradation level."""
    stripped = text.strip()

    # Holy grail: starts with asterisk and is bold+caps
    if stripped.startswith('*') and is_bold:
        return 'holy_grail'

    # For case checking, strip parenthetical annotations like "(key ingredient)"
    # and "esp." qualifiers — focus on the main pairing name
    base = re.sub(r'\s*\(.*?\)', '', stripped).strip()
    # Also strip "esp." and "e.g." qualifiers
    base = re.split(r',\s*esp\.', base)[0]
    base = re.split(r',\s*e\.g\.', base)[0]

    alpha_chars = re.sub(r'[^a-zA-Z]', '', base)
    is_all_caps = alpha_chars == alpha_chars.upper() and len(alpha_chars) > 0

    if is_bold and is_all_caps:
        return 'very_highly_recommended'
    elif is_bold:
        return 'recommended'
    else:
        return 'normal'


def is_main_entry_header(line):
    """Detect if a line is a main ingredient entry header.

    Main entries use a larger bold font (typically ~20pt or larger).
    The header name itself is all-caps, but may have parenthetical text
    like "(See also Basil, Thai, ...)" in mixed case.
    """
    text = line['text'].strip()
    if line['is_bold'] and line['avg_size'] > 17:
        # Strip parenthetical content before checking case
        base = re.sub(r'\s*\(.*\)', '', text).strip()
        alpha = re.sub(r'[^a-zA-Z]', '', base)
        if alpha == alpha.upper() and len(alpha) > 1:
            return True
    return False


def is_metadata_line(text):
    """Check if a line is metadata (Season, Taste, Weight, etc.)."""
    metadata_prefixes = [
        'Season:', 'Taste:', 'Function:', 'Weight:', 'Volume:',
        'Techniques:', 'Tips:', 'Botanical relatives:',
    ]
    for prefix in metadata_prefixes:
        if text.startswith(prefix):
            return True
    return False


def is_skip_line(text):
    """Detect lines that should be skipped: quotes, narrative, dishes, etc."""
    # Lines starting with common English sentence starters (quotes/narrative)
    sentence_starters = (
        'I ', '"', '\u201c', 'In ', 'If ', 'When ', 'The ', 'This ',
        'A ', 'My ', 'We ', 'For ', 'There ', 'It ', 'One ', 'Some ',
        'You ', 'As ', 'At ', 'But ', 'Since ', 'What ', 'Our ',
        'Do ', 'Try ', 'To ', 'Use ', 'Keep ', 'Not ', 'No ',
        'with ', 'and ', 'or ', 'from ', 'that ', 'these ',
        'an ', 'any ', 'about ', 'after ', 'also ', 'are ',
        'be ', 'been ', 'being ', 'both ', 'by ', 'can ',
        'could ', 'did ', 'does ', 'don', 'each ', 'every ',
        'few ', 'had ', 'has ', 'have ', 'he ', 'her ', 'here ',
        'his ', 'how ', 'into ', 'is ', 'its ', 'just ', 'like ',
        'make ', 'many ', 'may ', 'more ', 'most ', 'much ',
        'new ', 'now ', 'of ', 'on ', 'only ', 'other ',
        'out ', 'over ', 'own ', 'part ', 'put ', 'quite ',
        'really ', 'right ', 'same ', 'she ', 'should ', 'so ',
        'such ', 'than ', 'their ', 'them ', 'then ', 'there ',
        'very ', 'was ', 'way ', 'well ', 'were ', 'what ',
        'which ', 'while ', 'who ', 'why ', 'will ', 'would ',
    )
    if text.startswith(sentence_starters):
        return True

    # Em-dash (attribution lines like "— CHEF NAME")
    if '\u2014' in text or '—' in text:
        return True

    # "Dishes" header
    if text == 'Dishes':
        return True

    # "See also" references
    if text.startswith('(See') or text.startswith('See '):
        return True

    # Lines that look like dish descriptions (Title Case with proper names)
    # These tend to have multiple capitalized words in sequence
    if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z]', text) and '+' not in text:
        return True

    # Continuation of quotes: lines containing "[" brackets (editorial notes in quotes)
    if text.startswith('opposed ') or text.startswith('recipe '):
        return True

    # Lines that are clearly not food items (too many words, looks like prose)
    words = text.split()
    if len(words) > 8 and not any(text.startswith(x) for x in ('CHEESE', 'EGGS', 'APPLES')):
        return True

    # Short fragments that are clearly not food items
    if text.endswith('.') and len(words) <= 2 and not any(c.isupper() for c in text[:-1]):
        return True

    return False


def extract_pairings_for_ingredient(lines, start_idx):
    """Extract all pairings for an ingredient starting at the given header index."""
    header_line = lines[start_idx]
    ingredient = header_line['text'].strip()

    # Clean up ingredient name
    ingredient_clean = re.sub(r'\s*\(See also.*?\)', '', ingredient)
    ingredient_clean = re.sub(r'\s*\(See.*?\)', '', ingredient_clean)
    ingredient_clean = re.sub(r'\s*\(IN GENERAL\)', '', ingredient_clean)
    ingredient_clean = ingredient_clean.strip()

    pairings = []
    in_avoid = False
    in_flavor_affinities = False
    i = start_idx + 1

    while i < len(lines):
        line = lines[i]
        text = line['text'].strip()

        # Stop if we hit the next main entry header
        if is_main_entry_header(line):
            break

        # Skip metadata lines
        if is_metadata_line(text):
            i += 1
            continue

        # Skip empty or very short lines
        if len(text) < 2:
            i += 1
            continue

        # Detect AVOID section
        if text == 'AVOID':
            in_avoid = True
            in_flavor_affinities = False
            i += 1
            continue

        # Detect Flavor Affinities section
        if text.startswith('Flavor Affinities') or text.startswith('Flavor affinities'):
            in_flavor_affinities = True
            in_avoid = False
            i += 1
            continue

        # Skip flavor affinities lines (compound combinations with +)
        if in_flavor_affinities:
            i += 1
            continue

        # Skip quotes, narrative text, dish descriptions
        if is_skip_line(text):
            i += 1
            continue

        # Process pairing line
        if in_avoid:
            pairings.append({
                'pairing': text,
                'level': 'avoid',
                'page': line['page'],
            })
        else:
            level = classify_pairing(text, line['is_bold'])

            # Clean asterisk from holy grail pairings
            pairing_text = text.lstrip('*').strip() if level == 'holy_grail' else text

            pairings.append({
                'pairing': pairing_text,
                'level': level,
                'page': line['page'],
            })

        i += 1

    return ingredient_clean, pairings, i


def extract_sample(ingredients_to_find):
    """Extract pairings for specific sample ingredients."""
    pdf = pdfplumber.open(PDF_PATH)
    print(f"Scanning PDF ({len(pdf.pages)} pages)...")

    lines = extract_lines_with_font_info(pdf, 40, len(pdf.pages))

    results = {}
    found = set()

    i = 0
    while i < len(lines):
        line = lines[i]
        if is_main_entry_header(line):
            header_text = line['text'].strip()
            for target in ingredients_to_find:
                # Exact match: header must be exactly the target or target + " (See also..."
                header_base = re.sub(r'\s*\(.*', '', header_text).strip()
                if header_base == target.upper() and target not in found:
                    ingredient, pairings, end_idx = extract_pairings_for_ingredient(lines, i)
                    results[ingredient] = pairings
                    found.add(target)
                    i = end_idx
                    break
            else:
                i += 1
        else:
            i += 1

        if len(results) == len(ingredients_to_find):
            break

    pdf.close()
    return results


def extract_all():
    """Extract all pairings from the entire Chapter 3."""
    pdf = pdfplumber.open(PDF_PATH)

    print(f"Scanning all {len(pdf.pages)} pages...")
    lines = extract_lines_with_font_info(pdf, 40, len(pdf.pages))
    print(f"Extracted {len(lines)} lines with font info")

    # Non-ingredient headers to skip (book sections, chapter titles, etc.)
    skip_headers = {
        'FLAVOR MATCHMAKING: THE CHARTS',
        'MATCHING FLAVORS',
        'ACKNOWLEDGMENTS',
        'ABOUT THE EXPERTSM',
        'ABOUT THE AUTHORS',
        'ABOUT THE PHOTOGRAPHER',
        'ALSO BY THE AUTHORS',
    }

    all_results = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if is_main_entry_header(line):
            raw_header = line['text'].strip()
            header_text = re.sub(r'\s*\(.*?\)', '', raw_header).strip()
            # Fix known concatenation: "YAMS (See Sweet Potatoes) YOGURT"
            if 'YAMS' in raw_header and 'YOGURT' in raw_header:
                line['text'] = 'YOGURT'
                header_text = 'YOGURT'
            if header_text in skip_headers:
                i += 1
                continue
            ingredient, pairings, end_idx = extract_pairings_for_ingredient(lines, i)
            for p in pairings:
                all_results.append({
                    'ingredient': ingredient,
                    'pairing': p['pairing'],
                    'level': p['level'],
                    'page': p['page'],
                })
            i = end_idx
        else:
            i += 1

    pdf.close()
    return all_results


def save_to_csv(results, filename):
    """Save extraction results to CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ingredient', 'pairing', 'level', 'page'])
        for r in results:
            writer.writerow([r['ingredient'], r['pairing'], r['level'], r['page']])
    print(f"Saved {len(results)} pairings to {filename}")


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'sample'

    if mode == 'sample':
        samples = extract_sample(['BASIL', 'CINNAMON'])
        for ingredient, pairings in samples.items():
            print(f"\n{'='*60}")
            print(f"  {ingredient}")
            print(f"{'='*60}")
            for p in pairings:
                level_tag = f"[{p['level']}]"
                print(f"  {level_tag:30s} {p['pairing']:50s} (p.{p['page']})")
            print(f"  Total: {len(pairings)} pairings")

    elif mode == 'all':
        results = extract_all()
        save_to_csv(results, "/Users/marekkultys/Git Repos/spice/pairings.csv")

        ingredients = set(r['ingredient'] for r in results)
        print(f"\nExtracted {len(results)} total pairings for {len(ingredients)} ingredients")

        from collections import Counter
        levels = Counter(r['level'] for r in results)
        for level, count in sorted(levels.items()):
            print(f"  {level}: {count}")
