# mobile_testing.py
# Run with: python mobile_testing.py
# Model mobile testing scenarios using simulated device and application state.
# This does not operate a phone, render a layout, or measure real performance.

import unittest
from dataclasses import dataclass, field


# Group the device characteristics used by the scenarios.
# Values are supplied by the tests rather than read from hardware.
@dataclass
class Device:
    kind: str                    # Descriptive label: phone, tablet, foldable.
    width: int
    height: int
    orientation: str = "portrait"
    connectivity: str = "wifi"   # Expected labels: wifi, cellular, offline.
    battery_percent: int = 100
    text_scale: float = 1.0
    dark_mode: bool = False

    # Give each device an independent set of granted permissions.
    permissions: set[str] = field(default_factory=set)


# Represent application state and simplified rules for user actions.
@dataclass
class MobileApp:
    kind: str                    # Descriptive label: native, web, hybrid.
    installed: bool = False
    notifications_enabled: bool = True
    draft: str = ""

    # Keep mutable collections separate for each application instance.
    saved_tasks: list[str] = field(default_factory=list)
    analytics: list[dict] = field(default_factory=list)

    def install(self, available_storage_mb: int) -> bool:
        # Simulate installation requiring at least 50 MB of available storage.
        if available_storage_mb < 50:
            return False
        self.installed = True
        return True

    def enter_task(self, text: str, input_method: str) -> None:
        # Accept supported input-method labels and store the supplied text.
        # This does not invoke a keyboard, microphone, or clipboard.
        if input_method not in {"keyboard", "voice", "paste"}:
            raise ValueError("Unsupported input method")
        self.draft = text

    def save_task(self, device: Device) -> bool:
        # Preserve the draft when offline or when its title is blank.
        if device.connectivity == "offline" or not self.draft.strip():
            return False

        # Save the cleaned title in memory and record a local analytics event.
        title = self.draft.strip()
        self.saved_tasks.append(title)
        self.analytics.append({"event": "task_created", "title_length": len(title)})

        # Clear the draft only after a successful save.
        self.draft = ""
        return True

    def rotate(self, device: Device) -> None:
        # Swap dimensions and toggle orientation without changing the draft.
        device.width, device.height = device.height, device.width
        device.orientation = (
            "landscape" if device.orientation == "portrait" else "portrait"
        )

    def interrupt(self, interruption: str) -> None:
        # Validate the interruption label while deliberately preserving state.
        # No operating-system interruption is triggered.
        if interruption not in {"call", "alarm", "app_switch"}:
            raise ValueError("Unknown interruption")

    def use_camera(self, device: Device) -> bool:
        # Report whether the model grants camera access without capturing an image.
        return "camera" in device.permissions

    def notify(self, device: Device, message: str) -> bool:
        # Allow a modeled notification only when both settings permit it
        # and the message contains text. No notification is actually delivered.
        return (
            self.notifications_enabled
            and "notifications" in device.permissions
            and bool(message.strip())
        )

    def screen_is_usable(self, device: Device) -> bool:
        # Approximate available width after text scaling.
        # This illustrative threshold does not inspect rendered content.
        # The calculation assumes a positive, nonzero text scale.
        effective_width = device.width / device.text_scale
        return effective_width >= 280


class MobileTestScenarios(unittest.TestCase):
    def setUp(self):
        # Start each test with a fresh device and application.
        self.phone = Device(kind="phone", width=390, height=844)
        self.app = MobileApp(kind="hybrid", installed=True)

    def test_application_types(self):
        # Verify that each application-type label can be stored.
        # This does not test separate implementations of those application types.
        for kind in ("native", "web", "hybrid"):
            with self.subTest(kind=kind):
                app = MobileApp(kind=kind)
                self.assertEqual(app.kind, kind)

    def test_device_types_and_screen_sizes(self):
        # Apply the width rule to representative device dimensions.
        devices = [
            Device("phone", 390, 844),
            Device("tablet", 820, 1180),
            Device("foldable", 600, 900),
        ]
        for device in devices:
            with self.subTest(device=device.kind):
                self.assertTrue(self.app.screen_is_usable(device))

    def test_input_methods(self):
        # Confirm that supported input labels all preserve the supplied text.
        for method in ("keyboard", "voice", "paste"):
            with self.subTest(method=method):
                self.app.enter_task("Buy tickets", method)
                self.assertEqual(self.app.draft, "Buy tickets")

    def test_orientation_preserves_draft(self):
        # Rotate the device model and check that the draft remains intact.
        self.app.enter_task("Write README", "keyboard")
        self.app.rotate(self.phone)
        self.assertEqual(self.phone.orientation, "landscape")
        self.assertEqual(self.app.draft, "Write README")

    def test_interruptions_preserve_draft(self):
        # Check draft retention for each supported interruption label.
        for interruption in ("call", "alarm", "app_switch"):
            with self.subTest(interruption=interruption):
                self.app.enter_task("Finish testing", "keyboard")
                self.app.interrupt(interruption)
                self.assertEqual(self.app.draft, "Finish testing")

    def test_device_permission(self):
        # Verify camera access before and after granting permission in the model.
        self.assertFalse(self.app.use_camera(self.phone))
        self.phone.permissions.add("camera")
        self.assertTrue(self.app.use_camera(self.phone))

    def test_notifications(self):
        # Check permission denial, permission approval, and application opt-out.
        self.assertFalse(self.app.notify(self.phone, "Task due"))
        self.phone.permissions.add("notifications")
        self.assertTrue(self.app.notify(self.phone, "Task due"))
        self.app.notifications_enabled = False
        self.assertFalse(self.app.notify(self.phone, "Task due"))

    def test_connectivity_and_recovery(self):
        # Verify that an offline attempt retains the draft.
        self.app.enter_task("Write README", "keyboard")
        self.phone.connectivity = "offline"
        self.assertFalse(self.app.save_task(self.phone))
        self.assertEqual(self.app.draft, "Write README")

        # Restore connectivity and explicitly retry the save.
        # Recovery does not automatically submit the retained draft.
        self.phone.connectivity = "cellular"
        self.assertTrue(self.app.save_task(self.phone))
        self.assertIn("Write README", self.app.saved_tasks)

    def test_analytics_event(self):
        # Confirm that saving records the expected event and title length.
        self.app.enter_task("Test analytics", "keyboard")
        self.assertTrue(self.app.save_task(self.phone))
        self.assertEqual(
            self.app.analytics,
            [{"event": "task_created", "title_length": 14}],
        )

    def test_installability_and_storage(self):
        # Simulate insufficient storage followed by a successful installation.
        app = MobileApp(kind="native")
        self.assertFalse(app.install(20))
        self.assertFalse(app.installed)
        self.assertTrue(app.install(100))
        self.assertTrue(app.installed)

    def test_operating_system_preferences(self):
        # Store a dark-mode preference and evaluate width at increased text size.
        # No visual theme or actual operating-system setting is changed.
        self.phone.dark_mode = True
        self.phone.text_scale = 1.3
        self.assertTrue(self.phone.dark_mode)
        self.assertTrue(self.app.screen_is_usable(self.phone))

    def test_coexistence_with_another_app(self):
        # Model leaving the application while retaining an unfinished draft.
        self.app.enter_task("Keep my draft", "keyboard")
        self.app.interrupt("app_switch")
        self.assertEqual(self.app.draft, "Keep my draft")

    def test_usability_for_large_text(self):
        # Expect the width rule to flag this layout at 200% text scale.
        # Passing this test confirms detection of the modeled limitation.
        self.phone.text_scale = 2.0
        self.assertFalse(
            self.app.screen_is_usable(self.phone),
            "The modeled layout needs improvement at 200% text scale",
        )

    def test_simulated_power_budget(self):
        # Compare a manually assigned consumption value with a sample budget.
        # No battery usage is measured or attributed to application activity.
        battery_before = self.phone.battery_percent
        simulated_consumption = 3
        self.phone.battery_percent -= simulated_consumption
        self.assertLessEqual(
            battery_before - self.phone.battery_percent,
            5,
        )

    def test_response_time(self):
        # Compare fixed sample values rather than timing an operation.
        simulated_response_ms = 240
        target_ms = 500
        self.assertLess(simulated_response_ms, target_ms)


if __name__ == "__main__":
    # Discover and run the test methods, displaying each name and outcome.
    unittest.main(verbosity=2)