# mobile_testing_challenges.py
# Run with: python mobile_testing_challenges.py
# Check submission rules for screen width, connectivity, and task titles.

import unittest


def can_submit_task(title, screen_width, online):
    # Reject submission when the supplied width is below the minimum.
    if screen_width < 320:
        return False, "Screen too narrow to use the form"

    # Require a connection before allowing submission.
    if not online:
        return False, "No connection; task was not saved"

    # Reject empty titles, including those containing only whitespace.
    if not title.strip():
        return False, "Task title cannot be blank"

    # Indicate success when all checks pass.
    # This example simulates the outcome; it does not store a task.
    return True, "Task saved"


class MobileTestingChallenges(unittest.TestCase):
    def test_small_phone_screen(self):
        # Verify that the minimum supported width allows submission.
        saved, message = can_submit_task("Write README", 320, True)
        self.assertTrue(saved, message)

    def test_phone_after_rotation(self):
        # Check representative portrait and landscape widths.
        # These values test the rule, rather than physical device rotation.
        for width in (390, 844):
            with self.subTest(width=width):
                saved, message = can_submit_task("Write README", width, True)
                self.assertTrue(saved, message)

    def test_lost_connection(self):
        # Verify that an offline submission is rejected with clear feedback.
        saved, message = can_submit_task("Write README", 390, False)
        self.assertFalse(saved)
        self.assertEqual(message, "No connection; task was not saved")

    def test_blank_input_on_phone(self):
        # Verify that whitespace-only input is rejected on a supported screen.
        saved, message = can_submit_task("   ", 390, True)
        self.assertFalse(saved)
        self.assertEqual(message, "Task title cannot be blank")


if __name__ == "__main__":
    # Run all tests and display each test's name and result.
    unittest.main(verbosity=2)