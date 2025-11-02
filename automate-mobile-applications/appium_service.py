import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
import time
from typing import List
from .appium_capabilities import adventure_capitalist_capabilities

"""
Package names for games
Adventure communist: com.kongregate.mobile.adventurecommunist.google
adVenture capitalist: com.kongregate.mobile.adventurecapitalist.google
"""

# https://stackoverflow.com/questions/4032960/how-do-i-get-an-apk-file-from-an-android-device
# adb shell pm list packages
# adb shell pm path com.auxbrain.egginc
# adb pull /data/app/~~tweXlYiQgWJQJgvXJMtepw==/com.auxbrain.egginc-FWJI9t5kEQOcevIqVQZziA==/base.apk ./eggInc.apk
# https://stackoverflow.com/questions/12698814/get-launchable-activity-name-of-package-from-adb
# /Users/kvosburgh_mac/Library/Android/sdk/build-tools/31.0.0/aapt dump configurations eggInc.apk
# alternative below
# adb shell pm dump com.auxbrain.egginc | grep -A 1 MAIN

# get screenshot: adb exec-out screencap -p > screen.png


ANDROID_BASE_CAPS = {
    # 'app': os.path.abspath('../apps/ApiDemos-debug.apk'),
    "automationName": "UiAutomator2",
    "platformName": "Android",
    "platformVersion": os.getenv("ANDROID_PLATFORM_VERSION") or "12.0",
    # 'deviceName': os.getenv('ANDROID_DEVICE_VERSION') or 'Android Emulator',
    "name": "test-session",
    "appPackage": "com.auxbrain.egginc",
    "app": os.path.join(os.path.dirname(__file__), "eggInc.apk"),
    "udid": "RFCT70B6C8P",
    "appActivity": "com.auxbrain.egginc.EggIncActivity",
    "newCommandTimeout": 600,
    "noReset": True,
    "fullReset": False,
    "dontStopAppOnReset": True,
    "autoLaunch": True,
    "skipLogcatCapture": True,
}

EXECUTOR = "http://127.0.0.1:4723"


class AppiumService:

    long_press_coords: List[List[int]]
    tap_coords: List[List[int]]
    reapply_long_press: bool
    # used to try and get faster feedback for ongoing flows
    ignore_other_actions: bool

    def __init__(self) -> None:
        options = UiAutomator2Options().load_capabilities(
            adventure_capitalist_capabilities
        )

        self.driver = webdriver.Remote(EXECUTOR, options=options)
        self.long_press_coords = []
        self.tap_coords = []
        self.reapply_long_press = True
        self.ignore_other_actions = False
        print("done initializing")

    # Note that press_for_time is in milli-seconds
    def add_long_press_at_coords(self, x, y):
        # don't add coords if they have already been added. Shouldn't happen but the check is for just in case
        for coords in self.long_press_coords:
            if coords[0] == x and coords[1] == y:
                return
        self.reapply_long_press = True
        self.long_press_coords.append([x, y])

    def remove_long_press_at_coords(self, x, y):
        self.reapply_long_press = True
        for coord_index in range(len(self.long_press_coords)):
            current = self.long_press_coords[coord_index]
            if current[0] == x and current[1] == y:
                del self.long_press_coords[coord_index]
                return

    def add_tap_at_coords(self, x, y):
        # don't add coords if they have already been added. Shouldn't happen but the check is for just in case
        for coords in self.tap_coords:
            if coords[0] == x and coords[1] == y:
                return
        self.tap_coords.append([x, y])

    # def _long_press_at_coords(self):
    #     if len(self.long_press_coords) == 0 or not self.reapply_long_press:
    #         return

    #     print("APPIUM: long_press", self.reapply_long_press)
    #     action = TouchAction(self.driver)
    #     for coord in self.long_press_coords:
    #         print("\t", coord)
    #         action.long_press(x=coord[0], y=coord[1], duration=1)
    #     action.perform()

    # def _tap_at_coords(self):
    #     if len(self.tap_coords) == 0:
    #         return
    #     print("APPIUM: tapping")
    #     action = TouchAction(self.driver)
    #     for coord in self.tap_coords:
    #         print("\t", coord)
    #         action.tap(x=coord[0], y=coord[1], count=1)
    #     action.perform()

    #     self.reapply_long_press = True

    # def drag_from_to(self, from_coords, to_coords):
    #     action = TouchAction(self.driver)
    #     action.press(x=from_coords[0], y=from_coords[1])
    #     action.move_to(x=to_coords[0], y=to_coords[1])
    #     action.release()
    #     action.perform()

    #     self.reapply_long_press = True
    #     self.ignore_other_actions = True

    def do_actions(self):
        if self.ignore_other_actions:
            self.ignore_other_actions = False
            self.tap_coords = []
            return
        self._tap_at_coords()
        self.tap_coords = []
        self._long_press_at_coords()
        self.reapply_long_press = False

    def meaningless_tap(self):
        self.add_tap_at_coords(0, 2140)

    def get_page_source(self) -> str:
        return self.driver.page_source

    def cleanup(self):
        self.driver.quit()


if __name__ == "__main__":
    service = AppiumService()
    # driver.start_activity(ANDROID_BASE_CAPS['appPackage'], ANDROID_BASE_CAPS["appActivity"])
    for i in range(100):
        time.sleep(5)
        print("\n\n\n\n BLARG", i)
        print(service.get_page_source())

    service.cleanup()
    # time.sleep(10000)
