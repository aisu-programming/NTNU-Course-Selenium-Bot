""" Libraries """
import os
import time
from selenium.common.exceptions import WebDriverException
from seleniumwire import webdriver
import random
from utils import (
    BrowserStuckError,
    beep_sound, my_time_str,
    click_and_wait, wait_and_find_element_by_id,
    login,
)
from model import load_MyModel


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


def course_monitoring(driver, course_ids):

    start_time = time.time()

    while True:
        print(f"{my_time_str(start_time)} - The course ids list now:", course_ids, '\n')
        try:
            for course_id in course_ids:
                wait_and_find_element_by_id(driver, "serialNo-inputEl").clear()
                wait_and_find_element_by_id(driver, "serialNo-inputEl").send_keys(course_id)
                click_and_wait(wait_and_find_element_by_id(driver, "notFull-inputEl"))  # 「未額滿課程」checkbox
                time.sleep(0.2)
                click_and_wait(wait_and_find_element_by_id(driver, "button-1059-btnEl"))  # 「查詢」按鈕
                
                table  = wait_and_find_element_by_id(driver, "gridview-1113-body")
                trlist = table.find_elements_by_tag_name('tr')
                if len(trlist):
                    course_ids.remove(course_id)
                    print(f"{my_time_str(start_time)} - Course {course_id:.2} is available now!\n")
                    beep_sound()
                else:
                    random_second = 3 + 2 * random.random()
                    print(f"{my_time_str(start_time)} - Sleep for {random_second:.2} seconds.\n")
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

    # Load predict model
    model = load_MyModel()
    model.summary()

    # Read username, password and course ids
    try:    username, password, course_ids = read_account()
    except: return

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--auto-open-devtools-for-tabs")
    driver = webdriver.Chrome("chromedriver_win32/chromedriver.exe", chrome_options=options)

    while True:
        login(driver, username, password, model)
        course_monitoring(driver, course_ids)
        driver.delete_all_cookies()
        if len(course_ids) == 0: break
        time.sleep(10)
        print(f"\n{my_time_str()} - Restart a turn.\n")

    driver.close()
    return


""" Execution """
if __name__ == "__main__":
    main()