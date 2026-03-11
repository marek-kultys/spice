# Product Definition Document

### Product Name
Spice

### User Problem
Often, I would start cooking an improvised dish based around a single ingredient that I want to use. This cold be a main ingredient of the dish (for example, avocado in guacamole), or a secondary ingredient (for example, venison in a casserole). Since I am not following a defined recipe, I would then face the problem of not knowing what spices to use in my dish (for my unique combination of ingredients) to make the most of the available flavours, scents, and aromas. 

Without Spice, I would simply guess what spices to use, risking that the resulting dish would suffer due to bad spice pairing or dosing. With Spice, I get reliable recommendations what to pair with my ingredients to avoid disappointment and make the most of the ingredients.

### Product Summary
Spice is a personal mobile application that helps users pair spices and herbs with other food ingredients that they plan to use in their dish.

Spice is meant to be used in the moment or shortly before cooking as a source of reliable advice, inspiration, and reliable improvisation when cooking. It does not provide recipes that have a pre-defined combination of ingredients and spices. Instead, it provides seasoning recommendations for any combination of food ingredients at hand.

When using Spice, users input their food ingredients and their amounts (in kilograms or litres), and receive recommendations based on known food-spice pairing encoded in the database of the application. Spice recommendations will include the name of the spice or herb, as well as the recommended amount to be used (in grams or millilitres).

Users can input multiple ingredients and classify them as main ingredients. Spice will weight the responses based on this classification. Weighing will influence the prioritisation of pairing recommendations and recommended amounts.

Next to the list of recommended spice pairings, Spice will also provide a no-go list of spices and herbs that should not be used with the combination of selected ingredients.

Every spice recommendation is stored in the app. Users are able to favourite and retrieve the recommendations that they like.

### Feature list

##### List of Spice Recommendations
Users can access the list of all generated food-spice recommendations and:
##### Controlled Vocabulary List of Flavours
Underlying the entire system, there is a controlled Vocabulary List of flavours and ingredients defined in `/vocabulary.json` and used by the User and the Recommendation Engine. This list is centralised and no flavour or ingredient should be used in the app by the user of the system if it is not included in the Vocabulary List. All spelling should be consistent with the Vocabulary List.
1. Browse the list
2. Add the "favourite" tag on individual recommendations
3. Remove the "favourite" tag from individual recommendations
4. Delete individual recommendations
5. Filter the list by ingredient, spice, favourite status, and date
6. View an individual food-spice recommendation
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
Users can submit a query to generate a new food-spice recommendation and:
1. Enter the names of food ingredients (up to 5)
2. Mark selected ingredients as main (up to 2)
3. Enter the amounts for each food ingredient (in kilograms or litres)
4. Run the recommendation process
5. View the food-spice recommendation

##### View Recommendation
Users can open an existing food-spice recommendation and:
1. View the list of input food ingredients (including amounts and main marking)
2. View the list of recommended spices (with amounts)
3. View the list of spices to avoid (no-go)
4. Add the "favourite" tag to the recommendation
5. Delete the recommendation
6. Mark those of the recommended spices that are unavailable
7. Generate an alternative recommendation that avoids the use of unavailable spices

##### Recommendation Engine
Spice uses a fixed database of recommended food-spice pairings stored locally.

Spice consolidates individual food-spice pairings into a single recommendation based on the set of food ingredients inputed by the user. For example:
- Input: Avocado (main), Tomato, Onion
- Pairings: Avocado + coriander seeds, Avocado + lime juice, Avocado + vinegar, Tomato + salt, Tomato + coriander seeds, Tomato + black pepper, Onion + salt, Onion !+ vinegar
- Recommendation: coriander seeds, lime juice

### Product Non-Goals
This is what Spice will not do:
- provide full cooking recipes
- provide cooking instructions
- provide nutritional information
- support user accounts
- change pairing logic based on user action
- support any cloud-based capabilities
- connect online (this should be a fully stand-alone app)

### Data Model
