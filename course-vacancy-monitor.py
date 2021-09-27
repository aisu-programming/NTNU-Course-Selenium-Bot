""" Libraries """
import os
import time
import random
import requests
from seleniumwire import webdriver
from selenium.common.exceptions import WebDriverException
from utils import (
    BrowserStuckError,
    beep_sound, my_time_str,
    click_and_wait, wait_and_find_element_by_id,
    login,
)
from model import load_MyModel


""" Parameters """
LINE_NOTIFY_BOT = False


""" Functions """
def read_account():
    try:
        with open("account.txt", "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()
            if len(lines) < 3: raise Exception
            username   = lines[0].strip('\n')
            password   = lines[1].strip('\n')
            course_ids = list(filter(lambda id: '#' not in id, [ id.strip('\n') for id in lines[2:] ]))
        return username, password, course_ids
    except:
        with open("account.txt", "w", encoding="utf-8") as txt_file:
            txt_file.write("UsernameHere\nPasswordHere\nCourseId1\nCourseId2...")
        print("\nThe file 'account.txt' are created.")
        print("Please edit it before run this program again.\n")


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


def send_LineNotification(access_token, message):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {"message": message}
    requests.post(
        "https://notify-api.line.me/api/notify",
        headers=headers, params=params
    )
    return


def course_monitoring(driver, course_ids, access_token):

    start_time = time.time()
    if LINE_NOTIFY_BOT: send_LineNotification(access_token, f"\nStart a monitor turn.\nThe course ids list now:\n{course_ids}")

    click_and_wait(wait_and_find_element_by_id(driver, "notFull-inputEl"))  # 「未額滿課程」checkbox

    while True:
        print(f"{my_time_str(start_time)} | The course ids list now:", course_ids, '\n')
        try:
            for course_id in course_ids:
                wait_and_find_element_by_id(driver, "serialNo-inputEl").clear()
                wait_and_find_element_by_id(driver, "serialNo-inputEl").send_keys(course_id)
                time.sleep(0.2)
                click_and_wait(wait_and_find_element_by_id(driver, "button-1059-btnEl"))  # 「查詢」按鈕
                
                table  = wait_and_find_element_by_id(driver, "gridview-1113-body")
                trlist = table.find_elements_by_tag_name('tr')
                if len(trlist):
                    course_ids.remove(course_id)
                    print(f"{my_time_str(start_time)} | Course '{course_id}' is available now!\n")
                    if LINE_NOTIFY_BOT:
                        send_LineNotification(access_token, f"\nCourse '{course_id}' is available now!")
                    beep_sound()
                else:
                    random_second = 3 + 2 * random.random()
                    print(f"{my_time_str(start_time)} | Course '{course_id}' is full. Sleep for {random_second:.2} seconds.\n")
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
    try   : username, password, course_ids = read_account()
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
    driver = webdriver.Chrome("chromedriver_win32/chromedriver.exe", chrome_options=options)

    while True:
        login(driver, username, password, model)
        # if LINE_NOTIFY_BOT: send_LineNotification(access_token, f"\nMonitor started.")
        course_monitoring(driver, course_ids, access_token)
        driver.delete_all_cookies()
        if len(course_ids) == 0: break
        time.sleep(10)
        print(f"\n{my_time_str()} - Restart a turn.\n")

    driver.close()
    return


""" Execution """
if __name__ == "__main__":
    main()