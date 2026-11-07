"""Basic tests that do not require downloading any voice models."""
import unittest
from engine import reference_clip_ms, validate_input

class TestValidation(unittest.TestCase):
    def test_valid_text(self):
        self.assertEqual(validate_input(" Halo. "), "Halo.")
    def test_empty_text(self):
        with self.assertRaises(ValueError):
            validate_input(" ")
    def test_reference_transcript_required(self):
        with self.assertRaises(ValueError):
            validate_input("Halo", "")
    def test_reference_clip(self):
        self.assertEqual(reference_clip_ms(6.3, 40000), 6300)
        self.assertEqual(reference_clip_ms(6.3, 5000), 5000)
        with self.assertRaises(ValueError):
            reference_clip_ms(12, 20000)

if __name__ == "__main__":
    unittest.main()
