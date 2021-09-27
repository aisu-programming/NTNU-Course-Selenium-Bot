""" Libraries """
import io
import time
import winsound
import datetime
import numpy as np
from model import id_to_word, process_image


""" Functions """
class BrowserStuckError(Exception):
    pass


class CourseTakenException(Exception):
    pass


def beep_sound():
    for _ in range(5):
        winsound.Beep(800, 800)
        time.sleep(0.2)
    return


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
            else: return process_image(io.BytesIO(request.response.body))


def my_predict(model, image):
    image = np.array(np.expand_dims(image, axis=2), dtype=np.float)
    image = np.array([image])
    validate_code = model.predict(image)
    validate_code = np.squeeze(np.argmax(validate_code, axis=2))
    validate_code = [ id_to_word[id] for id in validate_code ]
    return validate_code


number_map = { str(i): i for i in range(10) }
def process_validate_code(validate_code):
    if '=' in validate_code:
        number_1 = number_map[validate_code[0]]
        number_2 = number_map[validate_code[2]]
        if   validate_code[1] == '+': return number_1 + number_2
        elif validate_code[1] == '-': return number_1 - number_2
        elif validate_code[1] == '*': return number_1 * number_2
    else:
        return ''.join(validate_code)


def my_time_str(start_time=None):
    if start_time is not None:
        interval = time.time() - start_time
        return f"{datetime.datetime.now().strftime(f'%H:%M:%S')} | {int(interval//60):>2}min {int(interval%60):>2}sec"
    else:
        return f"{datetime.datetime.now().strftime(f'%H:%M:%S')}"


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
            print(f"{my_time_str()} - Login: Validate code '{validate_code}' incorrect. Retry in 3 seconds.")
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