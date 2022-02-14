""" Libraries """
import os
import time
import random
from seleniumwire import webdriver
from selenium.common.exceptions import WebDriverException
from utils import (
    BrowserStuckError,
    beep_sound, send_LineNotification, my_time_str, read_account,
    wait_until_9_am, wait_to_click, wait_and_find_element_by_id,
    login,
)
from model import load_MyModel


""" Parameters """
LINE_NOTIFY_BOT = True


""" Functions """
def read_LineNotifyBot_AccessToken():
    try:
        with open("LineNotifyBot_AccessToken.txt", "r", encoding="utf-8") as txt_file:
            access_token = txt_file.readlines()[0].strip('\n')
            if access_token == "CopyYourAccessTokenHere": raise Exception
        return access_token
    except:
        with open("LineNotifyBot_AccessToken.txt", "w", encoding="utf-8") as txt_file:
            txt_file.write("CopyYourAccessTokenHere")
        print("\nThe file 'LineNotifyBot_AccessToken.txt' are created.")
        print("Please edit it before run this program again.\n")
        raise Exception


def course_monitoring(driver, access_token, course_ids, course_names=None):

    start_time = time.time()
    if LINE_NOTIFY_BOT:
        message = "\nThe courses list now:"
        if course_names is not None:
            for i in range(len(course_ids)): message += f"\n    {i+1}. {course_ids[i]}: {course_names[i]}"
        else:
            for i in range(len(course_ids)): message += f"\n    {i+1}. {course_ids[i]}"
        send_LineNotification(access_token, message)

    wait_to_click(wait_and_find_element_by_id(driver, "notFull-inputEl"))  # 「未額滿課程」checkbox

    while True:
        log = f"{my_time_str(start_time)} | The courses list now:\n"
        if course_names is not None:
            for i in range(len(course_ids)): log += f"    {i+1}. {course_ids[i]}: {course_names[i]}\n"
        else:
            for i in range(len(course_ids)): log += f"    {i+1}. {course_ids[i]}\n"
        print(log)
        try:
            for ci_i, course_id in enumerate(course_ids):
                wait_and_find_element_by_id(driver, "serialNo-inputEl").clear()
                wait_and_find_element_by_id(driver, "serialNo-inputEl").send_keys(course_id)
                time.sleep(0.2)
                wait_to_click(wait_and_find_element_by_id(driver, "button-1059-btnEl"))  # 「查詢」按鈕
                
                table  = wait_and_find_element_by_id(driver, "gridview-1113-body")
                trlist = table.find_elements_by_tag_name('tr')
                if len(trlist):
                    print(f"{my_time_str(start_time)} | Course {course_id}: '{course_names[ci_i]}' is available now!\n")
                    if LINE_NOTIFY_BOT:
                        send_LineNotification(access_token, f"\nCourse {course_id}: '{course_names[ci_i]}' is available now!")
                    course_ids.remove(course_id)
                    if course_names is not None: course_names.remove(course_names[ci_i])
                    beep_sound()
                else:
                    random_second = 3 + 2 * random.random()
                    print(f"{my_time_str(start_time)} | Course {course_id}: '{course_names[ci_i]}' is full. Sleep for {random_second:.2} seconds.\n")
                    time.sleep(random_second)

                if time.time() - start_time > 1170: break  # 19min 30sec

            if len(course_ids) == 0: break
            if time.time() - start_time > 1170: break  # 19min 30sec
        
        except BrowserStuckError:
            break

        except WebDriverException:
            break

    return


def main():

    # Check chromedriver
    if "chromedriver.exe" not in os.listdir("chromedriver_win32"):
        print("\nPlease download the chromedriver with corresponding version with " +
              "your Google Chrome at here:\nhttps://chromedriver.chromium.org/downloads\n"+
              "And put the 'chromedriver.exe'. in 'chromedriver_win32'\n")
        return

    # Read username, password and course ids
    try   : username, password, course_ids, course_names = read_account()
    except: return

    # Read LINE Notify Bot auth
    access_token = None
    if LINE_NOTIFY_BOT:
        try   : access_token = read_LineNotifyBot_AccessToken()
        except: return

    # Load predict model
    try   : model = load_MyModel()
    except: return
    model.summary()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--auto-open-devtools-for-tabs")

    while True:
        wait_until_9_am()
        driver = webdriver.Chrome("chromedriver_win32/chromedriver.exe", chrome_options=options)
        login(driver, username, password, model)
        course_monitoring(driver, access_token, course_ids, course_names)
        driver.delete_all_cookies()
        driver.close()
        if len(course_ids) == 0: break
        time.sleep(10)
        print(f"\n{my_time_str()} - Restart a turn.\n")

    return


""" Execution """
if __name__ == "__main__":
    main()