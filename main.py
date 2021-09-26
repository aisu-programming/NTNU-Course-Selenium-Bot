weights_file_path = "path/to/val_acc.h5"


# ================================================== #


""" Libraries """
import os
import time
import datetime
from selenium.common.exceptions import WebDriverException
from seleniumwire import webdriver
import io
import numpy as np
import random

from model import id_to_word, resize_image, load_MyModel


""" Dictionary """
number_map = { str(i): i for i in range(10) }


""" Functions """
def read_account():
    try:
        with open("account.txt", "r", encoding="utf-8") as txt_file:
            lines = txt_file.readlines()
            if len(lines) < 3: raise Exception
            username   = lines[0].strip('\n')
            password   = lines[1].strip('\n')
            course_ids = [ id.strip('\n') for id in lines[2:] ]
        return username, password, course_ids
    except:
        with open("account.txt", "w", encoding="utf-8") as txt_file:
            txt_file.write("UsernameHere\nPasswordHere\nCourseId1\nCourseId2...")
        print("\nThe file 'account.txt' are created.")
        print("Please edit it before run this program again.\n")


class BrowserStuckError(Exception):
    pass


class CourseTakenException(Exception):
    pass


def click_and_wait(element):
    for _ in range(25):
        try:
            element.click()
            time.sleep(1)
            return
        except:
            time.sleep(0.2)
    raise BrowserStuckError


def wait_for_url(driver, url_content):
    for _ in range(20):
        time.sleep(0.25)
        if url_content in driver.current_url: return
    raise BrowserStuckError


def wait_and_find_element_by_id(driver, id):
    for _ in range(25):
        try:
            element = driver.find_element_by_id(id)
            return element
        except:
            time.sleep(0.2)
    raise BrowserStuckError
    

def wait_appeared_element_by_id(driver):
    for _ in range(20):
        try:
            driver.find_element_by_id("button-1017-btnEl")
            return True
        except:
            pass
        try:
            click_and_wait(driver.find_element_by_id("button-1005-btnEl"))  # 「OK」按鈕
            return False
        except:
            time.sleep(0.5)
    raise BrowserStuckError


def wait_element_text_by_id(driver, id, texts):
    for _ in range(25):
        try:
            element = driver.find_element_by_id(id)
            for i, text in enumerate(texts):
                if text in element.text: return i  # return condition id
            raise CourseTakenException
        except:
            time.sleep(0.2)
    raise BrowserStuckError


def wait_for_validate_code_img(driver):
    for _ in range(25):
        if len(driver.find_elements_by_class_name("x-component-default")) == 10:
            return
        time.sleep(0.2)
    raise BrowserStuckError


def wait_for_validate_code_button(driver, button):
    for _ in range(25):
        buttons = driver.find_elements_by_class_name("x-btn-button")
        if len(buttons) == 19:
            if button == "confirm": return buttons[17]
            else                  : return buttons[18]
        time.sleep(0.2)
    raise BrowserStuckError


def get_validate_code_img(driver):
    for request in reversed(driver.requests):
        if "RandImage" in request.url:
            if request.response == None: return None
            else: return resize_image(io.BytesIO(request.response.body))


def my_predict(model, image):
    image = np.array(np.expand_dims(image, axis=2), dtype=np.float)
    image = np.array([image])
    validate_code = model.predict(image)
    validate_code = np.squeeze(np.argmax(validate_code, axis=2))
    validate_code = [ id_to_word[id] for id in validate_code ]
    return validate_code


def process_validate_code(validate_code):
    if '=' in validate_code:
        number_1 = number_map[validate_code[0]]
        number_2 = number_map[validate_code[2]]
        if   validate_code[1] == '+': return number_1 + number_2
        elif validate_code[1] == '-': return number_1 - number_2
        elif validate_code[1] == '*': return number_1 * number_2
    else:
        return ''.join(validate_code)


def login(driver, username, password, model):
    driver.get("https://cos3s.ntnu.edu.tw/AasEnrollStudent/LoginCheckCtrl?language=TW")
    wait_and_find_element_by_id(driver, "userid-inputEl").send_keys(username)
    wait_and_find_element_by_id(driver, "password-inputEl").send_keys(password)
    validate_code_img = get_validate_code_img(driver)
    validate_code = my_predict(model, validate_code_img)
    validate_code = process_validate_code(validate_code)
    wait_and_find_element_by_id(driver, "validateCode-inputEl").send_keys(validate_code)
    click_and_wait(wait_and_find_element_by_id(driver, "button-1016-btnEl"))  # 「登入」按鈕

    # 驗證碼: 正確 或 錯誤
    while True:
        if wait_appeared_element_by_id(driver): break
        else:
            time.sleep(3)
            click_and_wait(wait_and_find_element_by_id(driver, "redoValidateCodeButton-btnEl"))  # 「重新產生」按鈕
            wait_and_find_element_by_id(driver, "password-inputEl").send_keys(password)
            validate_code_img = get_validate_code_img(driver)
            validate_code = my_predict(model, validate_code_img)
            validate_code = process_validate_code(validate_code)
            wait_and_find_element_by_id(driver, "validateCode-inputEl").send_keys(validate_code)
            click_and_wait(wait_and_find_element_by_id(driver, "button-1016-btnEl"))  # 「登入」按鈕

    click_and_wait(wait_and_find_element_by_id(driver, "button-1017-btnEl"))  # 「下一頁」按鈕
    wait_and_find_element_by_id(driver, "now")
    driver.execute_script("document.getElementById('now').parentElement.remove()")  # 移除計時器
    driver.switch_to.frame(wait_and_find_element_by_id(driver, "stfseldListDo"))
    click_and_wait(wait_and_find_element_by_id(driver, "add-btnEl"))  # 「加選」按鈕
    return


def my_time_str(start_time=None):
    if start_time is not None:
        interval = time.time() - start_time
        return f"{datetime.datetime.now().strftime(f'%H:%M:%S')} - {int(interval//60):>2}min {int(interval%60):>2}sec"
    else:
        return f"{datetime.datetime.now().strftime(f'%H:%M:%S')}"


def course_taking(driver, course_ids, model):

    start_time = time.time()

    while True:

        print(f"{my_time_str(start_time)} - The course ids list now:", course_ids, '\n')

        try:
            for course_id in course_ids:
                driver.find_element_by_id("serialNo-inputEl").clear()
                driver.find_element_by_id("serialNo-inputEl").send_keys(course_id)
                time.sleep(0.2)

                # 驗證碼破圖
                while True:
                    click_and_wait(driver.find_element_by_id("button-1060-btnEl"))  # 「開課序號直接加選儲存」按鈕
                    wait_for_validate_code_img(driver)
                    validate_code_img = get_validate_code_img(driver)
                    if validate_code_img is not None:
                        break
                    else:
                        click_and_wait(wait_for_validate_code_button(driver, "cancel"))  # 「取消」按鈕
                        click_and_wait(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"))  # 「OK」按鈕
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code image broken. Retry in 3 seconds.")
                        time.sleep(3)

                validate_code = my_predict(model, validate_code_img)
                validate_code = process_validate_code(validate_code)
                wait_and_find_element_by_id(driver, "valid-inputEl").send_keys(validate_code)
                click_and_wait(wait_for_validate_code_button(driver, "confirm"))  # 「確認」按鈕

                # 驗證碼: 正確 或 錯誤
                while True:
                    condition = wait_element_text_by_id(driver, "messagebox-1001-displayfield-inputEl", ["驗證碼錯誤", "額滿", "儲存成功"])
                    if condition == 0:
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' incorrect. Retry in 3 seconds.")
                        click_and_wait(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"))  # 「OK」按鈕
                        time.sleep(3)

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

                    elif condition == 1:
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' correct. Full.")
                        break

                    elif condition == 2:
                        print(f"{my_time_str(start_time)} - Course {course_id}: Validate code '{validate_code}' correct. Success!")
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
    if not os.path.exists("chromedriver_win32") or "chromedriver.exe" not in os.listdir("chromedriver_win32"):
        print("\nPlease download the chromedriver with corresponding version with " +
              "your Google Chrome at here:\nhttps://chromedriver.chromium.org/downloads\n"+
              "You should get a folder named 'chromedriver_win32' after you unzip it.\n")
        return

    # Load predict model
    model = load_MyModel(weights_file_path)
    model.summary()

    # Read username, password and course ids
    try:    username, password, course_ids = read_account()
    except: return

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--auto-open-devtools-for-tabs")
    driver = webdriver.Chrome("chromedriver_win32\chromedriver.exe", chrome_options=options)

    while True:
        login(driver, username, password, model)
        course_ids = course_taking(driver, course_ids, model)
        driver.delete_all_cookies()
        if len(course_ids) == 0: break
        time.sleep(10)
        print(f"\n{my_time_str()} - Restart a turn.\n")

    print("\n\nSuccess! Finish all course taking tasks!\n\n")
    driver.close()


""" Execution """
if __name__ == "__main__":
    main()