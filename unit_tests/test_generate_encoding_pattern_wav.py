import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from src.media.wav import AudioWav

class TestGenerateEncodingPatternWav(unittest.TestCase):

    def test_generate_encoding_pattern_image(self):
        img = AudioWav(file="./media/audio/Cantus_Bellorum_extract_8.wav")

        result = img.generate_lsb_encoding_pattern(1, "1")
        expected = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Failed for nbit=1, pattern='1': Expected pattern {expected}, but got {result}")

        result = img.generate_lsb_encoding_pattern(2, "2")
        expected = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Failed for nbit=2, pattern='2': Expected pattern {expected}, but got {result}")

        result = img.generate_lsb_encoding_pattern(3, "12")
        expected = [1, 2, 3, 0, 0, 0, 0, 0, 4, 5, 6, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Failed for nbit=3, pattern='12': Expected pattern {expected}, but got {result}")

        result = img.generate_lsb_encoding_pattern(3, "21")
        expected = [4, 5, 6, 0, 0, 0, 0, 0, 1, 2, 3, 0, 0, 0, 0, 0]
        self.assertEqual(result, expected, f"Failed for nbit=3, pattern='21': Expected pattern {expected}, but got {result}")

        with self.assertRaises(Exception) as context: img.generate_lsb_encoding_pattern(4, "21")
        self.assertEqual(str(context.exception), "nbit must be between 1 and 3")

        with self.assertRaises(Exception) as context: img.generate_lsb_encoding_pattern(3, "213")
        self.assertEqual(str(context.exception), "pattern must only contains 12")

if __name__ == '__main__':
    unittest.main()
