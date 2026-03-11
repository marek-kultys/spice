# Product Definition Document

### Product Name
Flavours

### User Problem
Often, I would start cooking an improvised dish based around a single ingredient that I want to use. This could be a main ingredient of the dish (for example, avocado in guacamole), or a secondary ingredient (for example, venison in a casserole). Since I am not following a defined recipe, I would then face the problem of not knowing what flavours to use in my dish (for my unique combination of ingredients) to make the most of the available flavours, scents, and aromas. 

Without Flavours, I would simply guess what flavours to use, risking that the resulting dish would suffer due to bad flavour pairing or dosing. With Flavours, I get reliable recommendations what to pair with my ingredients to avoid disappointment and make the most of the ingredients.

### Product Summary
Flavours is a personal mobile application that helps users pair flavours with other food ingredients that they plan to use in their dish.

Flavours is meant to be used in the moment or shortly before cooking as a source of reliable advice, inspiration, and reliable improvisation when cooking. It does not provide recipes that have a pre-defined combination of ingredients, flavours. Instead, it provides seasoning recommendations for any combination of food ingredients at hand.

When using Flavours, users input their food ingredients and their amounts (in kilograms or litres), and receive recommendations based on known food-flavour pairing encoded in the database of the application. Flavours recommendations will include the name of the flavour, as well as the recommended amount to be used (in grams or millilitres).

Users can input multiple ingredients and classify them as main ingredients. Flavours will weigh the responses based on this classification. Weighing will influence the prioritisation of pairing recommendations and recommended amounts.

Next to the list of recommended flavour pairings, Flavours will also provide a no-go list of flavours that should not be used with the combination of selected ingredients.

Every flavour recommendation is stored in the app. Users are able to favourite and retrieve the recommendations that they like.

### Feature list

##### Controlled Vocabulary List of Flavours
Underlying the entire system, there is a controlled Vocabulary List of flavours and ingredients defined in `/vocabulary.json` and used by the User and the Recommendation Engine. This list is centralised and no flavour or ingredient should be used in the app by the user of the system if it is not included in the Vocabulary List. All spelling should be consistent with the Vocabulary List.

##### List of Flavours Recommendations
Users can access the list of all previously generated food-flavour recommendations and:
1. Browse the list
2. Add the "favourite" tag on individual recommendations
3. Remove the "favourite" tag from individual recommendations
4. Delete individual recommendations
5. Filter the list by ingredient, flavour, favourite status, and date
6. View an individual food-flavour recommendation

##### List of Personal Preferences
Users can access the list of personal preferences and dietary guidelines to be used by the Recommendation Engine:
1. Browse the list of entred preferences
2. Add new preferences
3. Delete existing preferences
4. Edit existing preferences
5. For each preferences in the list, the user can:
    - give it a title
    - select the flavour or ingredient from the controlled Vocabulary List
    - define if the preference is a subjective preference or a dietary requirement
    - for a subjective preference, users will define if it is a "Like" (in which case the ingredient will be upweighted by the Recommendation Engine) or a "Dislike" (in which case the ingredient will be downweighted by the Recommendation Engine)
    - for a dietary requirement, users will define if it is an "Allergy" or "Intolerance"; in both cases the ingredient will be removed from the results by the Recommendation Engine

##### Generate Recommendation
Users can submit a query to generate a new food-flavour recommendation and:
1. Enter the names of food ingredients (up to 5) with automatic grounding of entries to the Vocabulary List
2. Mark selected ingredients as main (up to 2)
3. Run the recommendation process
4. View the food-flavour recommendation

##### View Recommendation
Users can open an existing food-flavour recommendation and:
1. View the list of input food ingredients (including main marking)
2. View the list of recommended flavours 
3. View the list of flavours to avoid (no-go)
4. View the strenght of each flavour recommendation
5. Add the "favourite" tag to the recommendation
6. Delete the recommendation
7. All ingredient inputs and flavour recommendations will include labels surfacing the stored Personal Preferences

##### Recommendation Engine
Flavour's Recommendation Engine takes inputs provided in the user query (ingredients) and inputs stored on the system (Personal Preferences) as defined in `/object-schema.json` and using the logic described in `/engine.py` generates a recommendation for flavour pairings and flavours to avoid based on the fixed database of food-flavour pairings stored locally in: `/pairings.csv`.

### Product Non-Goals
This is what Flavours will not do:
- provide full cooking recipes
- provide cooking instructions
- provide nutritional information
- support user accounts
- change pairing logic based on user action
- support any cloud-based capabilities
- connect online (this should be a fully stand-alone app)

### Data Model
