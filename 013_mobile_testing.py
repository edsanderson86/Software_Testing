# mobile_testing_challenges.py
# Run with: python mobile_testing_challenges.py

import unittest


def can_submit_task(title, screen_width, online):
    if screen_width < 320:
        return False, "Screen too narrow to use the form"

    if not online:
        return False, "No connection; task was not saved"

    if not title.strip():
        return False, "Task title cannot be blank"

    return True, "Task saved"


class MobileTestingChallenges(unittest.TestCase):
    def test_small_phone_screen(self):
        saved, message = can_submit_task("Write README", 320, True)
        self.assertTrue(saved, message)

    def test_phone_after_rotation(self):
        for width in (390, 844):  # Portrait and landscape
            with self.subTest(width=width):
                saved, message = can_submit_task("Write README", width, True)
                self.assertTrue(saved, message)

    def test_lost_connection(self):
        saved, message = can_submit_task("Write README", 390, False)
        self.assertFalse(saved)
        self.assertEqual(message, "No connection; task was not saved")

    def test_blank_input_on_phone(self):
        saved, message = can_submit_task("   ", 390, True)
        self.assertFalse(saved)
        self.assertEqual(message, "Task title cannot be blank")


if __name__ == "__main__":
    unittest.main(verbosity=2)