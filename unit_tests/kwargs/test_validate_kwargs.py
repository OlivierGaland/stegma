#import sys,os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from src.kwargs import validate_kwargs  # à ajuster selon l’emplacement réel

class TestValidateKwargs(unittest.TestCase):

    def test_valid_mandatory_optional(self):
        profile = {
            "mandatory": ["a", "b"],
            "optional": [{"name": "c", "default": 42}]
        }

        @validate_kwargs(profile)
        def f(**kwargs):
            return kwargs

        result = f(a=1, b=2)
        self.assertEqual(result["c"], 42)
        self.assertEqual(result["a"], 1)
        self.assertEqual(result["b"], 2)

    def test_duplicate_in_sections(self):
        profile = {
            "mandatory": ["a"],
            "optional": [{"name": "a", "default": 1}]
        }

        @validate_kwargs(profile)
        def f(**kwargs):
            return kwargs
            
        with self.assertRaises(Exception) as cm: f(b=1)            
        self.assertIn("present in multiple sections", str(cm.exception))

        with self.assertRaises(Exception) as cm: f(a=1)            
        self.assertIn("present in multiple sections", str(cm.exception))

        with self.assertRaises(Exception) as cm: f()            
        self.assertIn("present in multiple sections", str(cm.exception))

    def test_missing_mandatory(self):
        profile = {
            "mandatory": ["a"]
        }

        @validate_kwargs(profile)
        def f(**kwargs):
            return kwargs

        with self.assertRaises(Exception) as cm:
            f(b=1)

        self.assertIn("Missing mandatory argument", str(cm.exception))

    def test_exclusive_match_single(self):
        profile = {
            "exclusive": [
                ["x", "y"],
                ["z"]
            ]
        }

        @validate_kwargs(profile)
        def f(**kwargs):
            return kwargs

        result = f(z=123)
        self.assertEqual(result["z"], 123)

    def test_exclusive_ambiguous_profiles(self):
        profile = {
            "exclusive": [
                ["x" , "y", {"name": "z", "default": 10}],
                ["x" , "y", {"name": "w", "default": 10}]
            ]
        }

        @validate_kwargs(profile)
        def f(**kwargs):
            return kwargs

        # Ambiguïté non résolue car les deux profils matchent et x seul n’est pas sous-ensemble strict
        with self.assertRaises(Exception) as cm: f(x=1, y=2)
        self.assertIn("Ambiguous exclusive profile match", str(cm.exception))

    def test_exclusive_resolve_by_subset(self):
        profile = {
            "exclusive": [
                ["x"],
                ["x", "y"]
            ]
        }

        @validate_kwargs(profile)
        def f(**kwargs):
            return kwargs

        # ["x"] ⊂ ["x", "y"] → on garde le plus long profil
        result = f(x=1, y=2)
        self.assertEqual(result["x"], 1)
        self.assertEqual(result["y"], 2)

    def test_ignore_section(self):
        profile = {
            "ignore": ["debug"],
            "mandatory": ["a"]
        }

        @validate_kwargs(profile)
        def f(**kwargs):
            return kwargs

        result = f(a=1, debug=True)
        self.assertEqual(result["a"], 1)
        self.assertIn("debug", result)

if __name__ == '__main__':
    unittest.main()
