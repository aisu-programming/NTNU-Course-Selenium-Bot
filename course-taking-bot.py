""" Libraries """
import os
import time
import random
from seleniumwire import webdriver
from selenium.common.exceptions import WebDriverException
from utils import (
    BrowserStuckError,
    beep_sound, my_time_str, read_account,
    wait_until_9_am, click_and_wait, wait_and_find_element_by_id, wait_element_text_by_id,
    wait_for_validate_code_img, get_validate_code_img, wait_for_validate_code_button,
    my_predict, process_validate_code,
    login,
)
from model import load_MyModel


""" Functions """
def course_taking(driver, model, course_ids, course_names=None):

    start_time = time.time()

    while True:
        print(f"{my_time_str(start_time)} - The course ids list now:", course_ids, '\n')
        try:
            for course_id in course_ids:
                wait_and_find_element_by_id(driver, "serialNo-inputEl").clear()
                wait_and_find_element_by_id(driver, "serialNo-inputEl").send_keys(course_id)
                time.sleep(0.2)

                # 驗證碼: 正確 或 錯誤
                while True:

                    # 驗證碼破圖
                    validate_code_img_broken_time = 0
                    while True:
                        click_and_wait(driver.find_element_by_id("button-1060-btnEl"))  # 「開課序號直接加選儲存」按鈕
                        wait_for_validate_code_img(driver)
                        validate_code_img = get_validate_code_img(driver)
                        if validate_code_img is not None:
                            break
                        else:
                            click_and_wait(wait_for_validate_code_button(driver, "cancel"))  # 「取消」按鈕
                            click_and_wait(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"))  # 「OK」按鈕
                            retry_time = validate_code_img_broken_time * 2 + 3
                            print(f"{my_time_str(start_time)} - Course {course_id}: Validate code image broken. Retry in {retry_time} seconds.")
                            time.sleep(retry_time)
                            validate_code_img_broken_time += 1
                    
                    validate_code = my_predict(model, validate_code_img)
                    validate_code = process_validate_code(validate_code)
                    wait_and_find_element_by_id(driver, "valid-inputEl").send_keys(validate_code)
                    click_and_wait(wait_for_validate_code_button(driver, "confirm"))  # 「確認」按鈕

                    condition = wait_element_text_by_id(driver, "messagebox-1001-displayfield-inputEl", ["驗證碼錯誤", "額滿", "衝堂", "重複登記", "儲存成功"])
                    if condition == 0:  # 驗證碼錯誤
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' incorrect. Retry in 3 seconds.")
                        click_and_wait(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"))  # 「OK」按鈕
                        time.sleep(3)

                    elif condition == 1:  # 額滿
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' correct. Full.")
                        break

                    elif condition == 2:  # 衝堂
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' correct. Conflict.")
                        beep_sound()
                        course_ids.remove(course_id)
                        break

                    elif condition == 3:  # 重複登記
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' correct. Duplicated.")
                        beep_sound()
                        course_ids.remove(course_id)
                        break

                    elif condition == 4:  # 儲存成功
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' correct. Success!")
                        beep_sound()
                        course_ids.remove(course_id)
                        break
                
                click_and_wait(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"))  # 「OK」按鈕
                random_second = 5 + 5 * random.random()
                print(f"{my_time_str(start_time)} - Sleep for {random_second:.2} seconds.\n")
                time.sleep(random_second)
                if time.time() - start_time > 1170: break  # 19min 30sec

            if len(course_ids) == 0: break
            if time.time() - start_time > 1170: break  # 19min 30sec
        
        except BrowserStuckError:
            break

        except WebDriverException:
            break

    return course_ids


def main():

    # Check chromedriver
    if "chromedriver.exe" not in os.listdir("chromedriver_win32"):
        print("\nPlease download the chromedriver with corresponding version with " +
              "your Google Chrome at here:\nhttps://chromedriver.chromium.org/downloads\n"+
              "And put the 'chromedriver.exe'. in 'chromedriver_win32'\n")
        return

    # Read username, password and course ids
    try:    username, password, course_ids, course_names = read_account()
    except: return

    # Load predict model
    model = load_MyModel()
    model.summary()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--auto-open-devtools-for-tabs")

    while True:
        wait_until_9_am()
        driver = webdriver.Chrome("chromedriver_win32/chromedriver.exe", chrome_options=options)
        login(driver, username, password, model)
        course_ids = course_taking(driver, model, course_ids, course_names)
        driver.delete_all_cookies()
        driver.close()
        if len(course_ids) == 0: break
        time.sleep(10)
        print(f"\n{my_time_str()} - Restart a turn.\n")

    print("\n\nSuccess! Finish all course taking tasks!\n\n")


""" Execution """
if __name__ == "__main__":
    main()