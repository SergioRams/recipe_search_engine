## Recipe Search Engine

Recipes search engine built using inverted indexes.  
Original data set available from: [Kaggle - recipes version 2](https://www.kaggle.com/hugodarwood/epirecipes/version/2)


The search engine checks the following parts of the recipe:  

- title
- categories
- ingredients
- directions

For instance, given the query "banana cheese" you would expect "Banana Layer Cake with Cream Cheese Frosting" in the results. Note search is not case sensitive and the words do not have to be next to one another, or in the same order as the search query.

There are three ordering modes to select from, each indicated by passing a string to the search function:  

__normal__ - Based simply on the number of times the search terms appear in the recipe. A score is calculated and the order is highest to lowest. The score sums the following terms:

- 8×  Number of times a query word appears in the title
- 4×  Number of times a query word appears in the categories
- 2×  Number of times a query word appears in the ingredients
- 1×  Number of times a query word appears in the directions

__simple__ - Tries to minimise the complexity of the recipe, for someone who is in a rush. Orders to minimise the number of ingredients multiplied by the numbers of steps in the instructions

__healthy__ - Order from lowest to highest by the cost function.

Example
```python
engine = RecipeSearchEngine('recipes')

engine.search('Fish and Chips', ordering='normal')
engine.search('Banana cheese pie', ordering='simple')
engine.search('Apple pie', ordering='simple')
engine.search('Apple Pie Honey', ordering='healthy', details=True)
```

```buildoutcfg
Normal results for ['fish', 'chips'] are:

Fish and Chips with Tarragon-Malt Vinegar Mayonnaise  - id:1681 
Fish-and-Chips  - id:8261 
Fish-and-Chips  - id:11091 
Fish and Chips with Malt Vinegar Mayonnaise  - id:5587 
"Fish and Chips"  - id:3951 
Smoked Fish with Cucumber "Noodles"  - id:15380 
Barramundi Fillets With Roasted Sweet Potatoes and Brussels Sprout Chips  - id:4664 
Smoked Peppered Mackerel and Sour Cream on Homemade Potato Chips  - id:10327 
Ceviche Acapulqueño  - id:1169 
Cedar-Planked Char with Wood-Grilled Onions  - id:14640 
```

