import unittest
from src.media.image import PngRgbaImage

class TestGenerateEncodingPatternImage(unittest.TestCase):

    def test_generate_encoding_pattern_image(self):
        img = PngRgbaImage(file="./media/image/fantasy_micro.png")

        result = img.generate_lsb_encoding_pattern(1, "RGB")
        expected = [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=1, pattern='RGB'")

        result = img.generate_lsb_encoding_pattern(2, "RGB")
        expected = [1, 2, 0, 0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 0, 0, 0, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=2, pattern='RGB'")

        result = img.generate_lsb_encoding_pattern(3, "RGBA")
        expected = [1, 2, 3, 0, 0, 0, 0, 0, 4, 5, 6, 0, 0, 0, 0, 0, 7, 8, 9, 0, 0, 0, 0, 0, 10, 11, 12, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=3, pattern='RGBA'")

        result = img.generate_lsb_encoding_pattern(1, "BGR")
        expected = [3, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=1, pattern='BGR'")

        result = img.generate_lsb_encoding_pattern(2, "BGR")
        expected = [5, 6, 0, 0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=2, pattern='BGR'")

        result = img.generate_lsb_encoding_pattern(3, "BGR")
        expected = [7, 8, 9, 0, 0, 0, 0, 0, 4, 5, 6, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=3, pattern='BGR'")

        result = img.generate_lsb_encoding_pattern(1, "RGBA")
        expected = [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=1, pattern='RGBA'")

        result = img.generate_lsb_encoding_pattern(2, "RGBA")
        expected = [1, 2, 0, 0, 0, 0, 0, 0, 3, 4, 0, 0, 0, 0, 0, 0, 5, 6, 0, 0, 0, 0, 0, 0, 7, 8, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=2, pattern='RGBA'")

        result = img.generate_lsb_encoding_pattern(3, "RGBA")
        expected = [1, 2, 3, 0, 0, 0, 0, 0, 4, 5, 6, 0, 0, 0, 0, 0, 7, 8, 9, 0, 0, 0, 0, 0, 10, 11, 12, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Expected {expected} but got {result} for nbit=3, pattern='RGBA'")

if __name__ == '__main__':
    unittest.main()
