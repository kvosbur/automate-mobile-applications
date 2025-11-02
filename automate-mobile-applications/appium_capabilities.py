import os

egg_inc_capabilities = {
    # 'app': os.path.abspath('../apps/ApiDemos-debug.apk'),
    "automationName": "UiAutomator2",
    "platformName": "Android",
    "platformVersion": os.getenv("ANDROID_PLATFORM_VERSION") or "16.0",
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


# adb shell pm dump com.kongregate.mobile.adventurecapitalist.google| grep -A 1 MAIN
adventure_capitalist_capabilities = {
    # 'app': os.path.abspath('../apps/ApiDemos-debug.apk'),
    "automationName": "UiAutomator2",
    "platformName": "Android",
    "platformVersion": os.getenv("ANDROID_PLATFORM_VERSION") or "16.0",
    # 'deviceName': os.getenv('ANDROID_DEVICE_VERSION') or 'Android Emulator',
    "name": "test-session",
    "appPackage": "com.kongregate.mobile.adventurecapitalist.google",
    "app": os.path.join(os.path.dirname(__file__), "..", "apks", "advCapitalist.apk"),
    "udid": "emulator-5554",
    "appActivity": "com.kongregate.mobile.adventurecapitalist.google/com.clevertap.unity.CleverTapOverrideActivity",
    "newCommandTimeout": 600,
    "noReset": True,
    "fullReset": False,
    "dontStopAppOnReset": True,
    "autoLaunch": True,
    "skipLogcatCapture": True,
}
