import json
import re
import collections
import os.path
import pickle
from pprint import pprint
from nltk.corpus import stopwords
import nltk
# nltk.download('stopwords')


class RecipeSearchEngine:
    """
    Recipe search engine
    """
    # search weight values per section for 'normal' search
    title_value = 8
    categories_value = 4
    ingredients_value = 2
    directions_value = 1

    def __init__(self, file_name='recipes'):
        """
        reads 'recipes.json' file
        Data set origin: https://www.kaggle.com/hugodarwood/epirecipes/version/2
        :return: recipes (json)
        """

        # a dictionary to hold possible search sections
        self.inverted_index_dict = {'title_dict': {},
                                    'categories_dict': {},
                                    'ingredients_dict': {},
                                    'directions_dict': {},
                                    }
        # read json file
        with open(file_name+'.json') as f:
            self.recipes = json.load(f)

        if os.path.isfile('inverted_index.pickle'):
            # Load inverted index if exists
            with open('inverted_index.pickle', 'rb') as handle:
                self.inverted_index_dict = pickle.load(handle)

        else:
            # builds the inverted index dictionary
            self.build_inverted_index(self.recipes)
            # Store inverted index
            with open('inverted_index.pickle', 'wb') as handle:
                pickle.dump(self.inverted_index_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def print_recipe(self, recipe_index, details=True):
        """
        uses pprint to print recipes in a readable output
        :param recipe_index:
        :param details: if False prints title only, else prints whole recipe
        :return:
        """
        if details:
            pprint(self.recipes[recipe_index])
        else:
            print(f'{self.recipes[recipe_index]["title"]} - id:{recipe_index} ')

    @staticmethod
    def tokenize(sentence):
        """"
        helper function, tokenize each word of the given sentence, will also ignore special characters and digits via
        regex, lastly it will convert all characters into lower case.
        :return: tokens (list)
        """
        # regex to ignore digits and special characters
        sentence = re.sub(r'\W|\d', ' ', sentence)
        # turn string into a list of lower case tokens
        tokens = sentence.lower().split()

        return tokens

    def build_inverted_index(self, recipes):
        """
        Creates inverted index, for every word in title, categories, ingredients, directions and
        recipe simplicity, will ignore any recipe with no title.
        """

        # loop every recipe and builds inverted index for each section
        for document_idx, recipe in enumerate(recipes):
            self.title_dictionary(document_idx, recipe)
            self.build_dictionary(document_idx, recipe, 'categories',
                                  self.inverted_index_dict['categories_dict'],  RecipeSearchEngine.categories_value)
            self.build_dictionary(document_idx, recipe, 'ingredients',
                                  self.inverted_index_dict['ingredients_dict'],  RecipeSearchEngine.ingredients_value)
            self.build_dictionary(document_idx, recipe, 'directions',
                                  self.inverted_index_dict['directions_dict'], RecipeSearchEngine.directions_value)

    def title_dictionary(self, idx, recipe):
        """
        Builds inverted dictionary for title section
        :param idx: document index
        :param recipe: input containing recipe data
        :return:
        """
        # check if document has a title, else ignore it
        if 'title' in recipe:
            # tokenize each word in title and store them in title dictionary/index
            for word in RecipeSearchEngine.tokenize(recipe['title']):
                if word not in self.inverted_index_dict['title_dict']:
                    self.inverted_index_dict['title_dict'][word] = {}
                # add document index to dictionary along the search weight value
                if idx in self.inverted_index_dict['title_dict'][word]:
                    self.inverted_index_dict['title_dict'][word][idx] += RecipeSearchEngine.title_value
                else:
                    self.inverted_index_dict['title_dict'][word][idx] = RecipeSearchEngine.title_value

    def build_dictionary(self, doc_idx, recipe, section, dictionary, search_value):
        """
        :param doc_idx: document index
        :param recipe: input containing recipe data
        :param section: title, category, ingredients or directions
        :param dictionary: dictionary to save inverted index
        :param search_value: weight value defined  for each section
        :return:
        """
        # check if the section exists in the recipe
        if section in recipe:
            for sentence in recipe[section]:
                # tokenize each sentence into words and build a 'word: document index' dictionary
                for word in RecipeSearchEngine.tokenize(sentence):
                    if word not in dictionary:
                        dictionary[word] = {}

                    if doc_idx in dictionary[word]:
                        dictionary[word][doc_idx] += search_value  # add search value for 'normal' search
                    else:
                        dictionary[word][doc_idx] = search_value

    def global_search(self, query):
        """
        Common search method used by all other search methods, the idea is to search all the inverted indexes for every
        word, then create a set of matching recipe IDs and find and return the intersecting IDs.
        :param query:
        :return: a set of matching recipes IDs containing all words in search query
        """

        # dictionary holding a set of the matching recipes for each word
        section_match_dict = {}

        for word in query:
            for section in self.inverted_index_dict.keys():

                if word in self.inverted_index_dict[section].keys():  # avoids Key error
                    for recipe_idx in self.inverted_index_dict[section][word].keys():

                        if word not in section_match_dict:
                            section_match_dict[word] = {recipe_idx}
                        else:
                            section_match_dict[word].add(recipe_idx)

        # find intersections from all matching word - recipes_id
        recipe_words_intersect = set.intersection(*section_match_dict.values())
        return recipe_words_intersect

    def simple_search(self, recipes_idx):
        """
        simple search - Tries to minimise the complexity of the recipe, for someone who is in a rush.
        Orders to minimise the number of ingredients multiplied by the numbers of steps in the directions.
        """

        recipe_score = {}

        # loops all matching recipes
        for idx in recipes_idx:
            num_ingredients = len(self.recipes[idx]['ingredients'])
            num_steps = len(self.recipes[idx]['directions'])
            recipe_score[idx] = num_ingredients * num_steps

        return recipe_score

    def normal_search(self, recipes_idx, query):
        """
        Global search used by all other search to get recipes.
        returns sets of matching words on 4 indexed fields
        """

        recipe_score = {}

        for word in query:
            for section in self.inverted_index_dict.keys():
                for idx in recipes_idx:
                    # avoid KeyError
                    if (word in self.inverted_index_dict[section]) and (idx in self.inverted_index_dict[section][word]):
                        if idx not in recipe_score:
                            recipe_score[idx] = self.inverted_index_dict[section][word][idx]
                        else:
                            recipe_score[idx] += self.inverted_index_dict[section][word][idx]

        return recipe_score

    def healthy_search(self, recipes_idx):
        """
        healthy - Order from lowest to highest by this cost function.
        """

        recipe_score = {}

        # try n1,n2...n99, on valid recipes non-null parameters
        for idx in recipes_idx:

            # required for calculation:
            best_healthiness = 9 ** 9

            # ignore None values
            if self.recipes[idx]['calories'] and self.recipes[idx]['protein'] and self.recipes[idx]['fat']:
                for n in range(1, 100):
                    healthiness = (abs(self.recipes[idx]['calories'] - (510 * n)) / 510 +
                                   2 * abs(self.recipes[idx]['protein'] - (18 * n)) / 18 +
                                   4 * abs(self.recipes[idx]['fat'] - (150 * n)) / 150)

                    if healthiness < best_healthiness:
                        best_healthiness = healthiness
                    else:
                        recipe_score[idx] = best_healthiness
                        break

        return recipe_score

    def sort_dictionary_by_value(self, dictionary, n=10, descending=True):
        """
        sort results and returns top N best results
        :param dictionary:
        :param n: number of top results
        :param descending: sort order
        :return: list of tuples containing (doc index, total search value)
        """

        # sort results in descending order (highest to lowest)
        sorted_dict = [(k, dictionary[k]) for k in sorted(dictionary, key=dictionary.get, reverse=descending)]
        top_results = sorted_dict[:n]

        return top_results

    def search(self, query, ordering='normal', details=False):
        """
        Search function: able to search given 1 out of 3 possible search options: normal, simple and healthy.
        :param query: input query search
        :param ordering: Normal, Simple or Healthy
        :param details: False prints recipe title and index only, True prints the whole document
        :return:
        """
        top_results = []
        stop_words = stopwords.words('english')
        # tokenize and removes stop words
        query = RecipeSearchEngine.tokenize(query)
        query = [word for word in query if word not in stop_words]

        # ordering choices:
        if ordering == 'normal':
            all_results = self.normal_search(self.global_search(query), query)
            top_results = self.sort_dictionary_by_value(all_results, n=10, descending=True)
        elif ordering == 'simple':
            all_results = self.simple_search(self.global_search(query))
            top_results = self.sort_dictionary_by_value(all_results, n=10, descending=False)
        elif ordering == 'healthy':
            all_results = self.healthy_search(self.global_search(query))
            top_results = self.sort_dictionary_by_value(all_results, n=10, descending=False)

        print(f'{ordering.title()} results for {query} are:\n')
        for result in top_results:
            self.print_recipe(result[0], details=details)
        print('~~~*~~~'*15)


engine = RecipeSearchEngine('recipes')

engine.search('Fish and Chips', ordering='normal', details=False)
engine.search('Banana cheese', ordering='normal', details=False)
engine.search('Banana cheese pie', ordering='simple', details=False)
engine.search('Apple pie', ordering='simple', details=False)
engine.search('Apple Pie Honey', ordering='healthy', details=False)

