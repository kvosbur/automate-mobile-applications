from .appium_service import AppiumService
import time

service = AppiumService()
# driver.start_activity(ANDROID_BASE_CAPS['appPackage'], ANDROID_BASE_CAPS["appActivity"])
for i in range(100):
    time.sleep(5)
    print("\n\n\n\n BLARG", i)
    print(service.get_page_source())

service.cleanup()
