import unittest
import search


class TestSearch(unittest.TestCase):
    engine = search.RecipeSearchEngine('recipes')

    def test_tokenize(self):
        tokens = search.RecipeSearchEngine.tokenize('This iS a TesT')
        self.assertEqual(tokens, ['this', 'is', 'a', 'test'])

        tokens = search.RecipeSearchEngine.tokenize('This Contains Numbers 23, 44 and characters @ * )')
        self.assertEqual(tokens, ['this', 'contains', 'numbers', 'and', 'characters'])

    def test_normal_search_values(self):

        # calculation by hand, normal search value for recipe 63 with apple search is 12
        self.assertEqual(self.engine.inverted_index_dict['title_dict']['apple'][63], 8)
        self.assertEqual(self.engine.inverted_index_dict['ingredients_dict']['apple'][63], 2)
        self.assertEqual(self.engine.inverted_index_dict['directions_dict']['apple'][63], 2)
