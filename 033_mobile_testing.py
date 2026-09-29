# mobile_testing.py
# Run with: python mobile_testing.py
# A runnable scenario model. It simulates mobile conditions;
# it does not control a physical phone or collect real battery data.

import unittest
from dataclasses import dataclass, field


@dataclass
class Device:
    kind: str                    # phone, tablet, foldable
    width: int
    height: int
    orientation: str = "portrait"
    connectivity: str = "wifi"   # wifi, cellular, offline
    battery_percent: int = 100
    text_scale: float = 1.0
    dark_mode: bool = False
    permissions: set[str] = field(default_factory=set)


@dataclass
class MobileApp:
    kind: str                    # native, web, hybrid
    installed: bool = False
    notifications_enabled: bool = True
    draft: str = ""
    saved_tasks: list[str] = field(default_factory=list)
    analytics: list[dict] = field(default_factory=list)

    def install(self, available_storage_mb: int) -> bool:
        if available_storage_mb < 50:
            return False
        self.installed = True
        return True

    def enter_task(self, text: str, input_method: str) -> None:
        if input_method not in {"keyboard", "voice", "paste"}:
            raise ValueError("Unsupported input method")
        self.draft = text

    def save_task(self, device: Device) -> bool:
        if device.connectivity == "offline" or not self.draft.strip():
            return False

        title = self.draft.strip()
        self.saved_tasks.append(title)
        self.analytics.append({"event": "task_created", "title_length": len(title)})
        self.draft = ""
        return True

    def rotate(self, device: Device) -> None:
        device.width, device.height = device.height, device.width
        device.orientation = (
            "landscape" if device.orientation == "portrait" else "portrait"
        )

    def interrupt(self, interruption: str) -> None:
        if interruption not in {"call", "alarm", "app_switch"}:
            raise ValueError("Unknown interruption")
        # The draft is deliberately kept while the app loses focus.

    def use_camera(self, device: Device) -> bool:
        return "camera" in device.permissions

    def notify(self, device: Device, message: str) -> bool:
        return (
            self.notifications_enabled
            and "notifications" in device.permissions
            and bool(message.strip())
        )

    def screen_is_usable(self, device: Device) -> bool:
        effective_width = device.width / device.text_scale
        return effective_width >= 280


class MobileTestScenarios(unittest.TestCase):
    def setUp(self):
        self.phone = Device(kind="phone", width=390, height=844)
        self.app = MobileApp(kind="hybrid", installed=True)

    def test_application_types(self):
        for kind in ("native", "web", "hybrid"):
            with self.subTest(kind=kind):
                app = MobileApp(kind=kind)
                self.assertEqual(app.kind, kind)

    def test_device_types_and_screen_sizes(self):
        devices = [
            Device("phone", 390, 844),
            Device("tablet", 820, 1180),
            Device("foldable", 600, 900),
        ]
        for device in devices:
            with self.subTest(device=device.kind):
                self.assertTrue(self.app.screen_is_usable(device))

    def test_input_methods(self):
        for method in ("keyboard", "voice", "paste"):
            with self.subTest(method=method):
                self.app.enter_task("Buy tickets", method)
                self.assertEqual(self.app.draft, "Buy tickets")

    def test_orientation_preserves_draft(self):
        self.app.enter_task("Write README", "keyboard")
        self.app.rotate(self.phone)
        self.assertEqual(self.phone.orientation, "landscape")
        self.assertEqual(self.app.draft, "Write README")

    def test_interruptions_preserve_draft(self):
        for interruption in ("call", "alarm", "app_switch"):
            with self.subTest(interruption=interruption):
                self.app.enter_task("Finish testing", "keyboard")
                self.app.interrupt(interruption)
                self.assertEqual(self.app.draft, "Finish testing")

    def test_device_permission(self):
        self.assertFalse(self.app.use_camera(self.phone))
        self.phone.permissions.add("camera")
        self.assertTrue(self.app.use_camera(self.phone))

    def test_notifications(self):
        self.assertFalse(self.app.notify(self.phone, "Task due"))
        self.phone.permissions.add("notifications")
        self.assertTrue(self.app.notify(self.phone, "Task due"))
        self.app.notifications_enabled = False
        self.assertFalse(self.app.notify(self.phone, "Task due"))

    def test_connectivity_and_recovery(self):
        self.app.enter_task("Write README", "keyboard")
        self.phone.connectivity = "offline"
        self.assertFalse(self.app.save_task(self.phone))
        self.assertEqual(self.app.draft, "Write README")

        self.phone.connectivity = "cellular"
        self.assertTrue(self.app.save_task(self.phone))
        self.assertIn("Write README", self.app.saved_tasks)

    def test_analytics_event(self):
        self.app.enter_task("Test analytics", "keyboard")
        self.assertTrue(self.app.save_task(self.phone))
        self.assertEqual(
            self.app.analytics,
            [{"event": "task_created", "title_length": 14}],
        )

    def test_installability_and_storage(self):
        app = MobileApp(kind="native")
        self.assertFalse(app.install(20))
        self.assertFalse(app.installed)
        self.assertTrue(app.install(100))
        self.assertTrue(app.installed)

    def test_operating_system_preferences(self):
        self.phone.dark_mode = True
        self.phone.text_scale = 1.3
        self.assertTrue(self.phone.dark_mode)
        self.assertTrue(self.app.screen_is_usable(self.phone))

    def test_coexistence_with_another_app(self):
        self.app.enter_task("Keep my draft", "keyboard")
        self.app.interrupt("app_switch")
        self.assertEqual(self.app.draft, "Keep my draft")

    def test_usability_for_large_text(self):
        self.phone.text_scale = 2.0
        self.assertFalse(
            self.app.screen_is_usable(self.phone),
            "The modeled layout needs improvement at 200% text scale",
        )

    def test_simulated_power_budget(self):
        battery_before = self.phone.battery_percent
        simulated_consumption = 3
        self.phone.battery_percent -= simulated_consumption
        self.assertLessEqual(
            battery_before - self.phone.battery_percent,
            5,
        )

    def test_response_time(self):
        # A deterministic simulated response time, not a device benchmark.
        simulated_response_ms = 240
        target_ms = 500
        self.assertLess(simulated_response_ms, target_ms)


if __name__ == "__main__":
    unittest.main(verbosity=2)