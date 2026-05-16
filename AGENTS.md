# Admin Rules for AI agents and models

Code style preferences - SwiftUI patterns, naming conventions
Testing requirements - What should be tested before you accept code
File organization - How to structure the Xcode project
Error handling - How the app should behave when data is missing/corrupt
Version control - Commit message format, branching strategy


### Project structure
- ingredient vocabulary and ontology live in `vocabulary.json`
- ingredient pairing data lives in `pairings.json`
- see `product-definition.md` for the purpose and description of this app


### Do
- Default to small components. prefer focused modules over god components.
- Default to small files and diffs. Avoid repo-wide rewrites unless asked.
- Only use `/vocabulary.json` as source of ingredients. Only use `/pairings.json` as source of ingredient pairings.
- Store all style primitives (colours, font sizes, paddings, margins, border widths) as variables.


### Don't
- Do not hard-code colors.
- Do not add new heavy dependencies without approval.
- Do not make up ingredients or pairings.
- Do not make up data. If data is missing, corrupt, or incomplete, flag this before implementing anything.


### Safety and permissions
Allowed without prompt:
- read files, list files
- tsc single file, prettier, eslint,
- vitest single test

Ask first: 
- package installs,
- git push
- deleting files, chmod
- running full build or end to end suites