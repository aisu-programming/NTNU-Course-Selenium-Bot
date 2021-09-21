""" Libraries """
import time
import random
import selenium.webdriver
# from selenium.webdriver.chrome.options import Options
import packet


""" Parameters """
# None


""" Functions """
def wait_for_url(driver, url_content):
    while True:
        time.sleep(0.5)
        if url_content in driver.current_url: break
    return


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
        print("Please edit it before run this program again.")


def login(driver, username, password):
    driver.get("https://cos1s.ntnu.edu.tw/AasEnrollStudent/LoginCheckCtrl?language=TW")
    driver.find_element_by_id("userid-inputEl").send_keys(username)
    driver.find_element_by_id("password-inputEl").send_keys(password)
    wait_for_url(driver, "IndexCtrl")
    driver.find_element_by_id("button-1017-btnEl").click()  # 「下一頁」按鈕
    wait_for_url(driver, "EnrollCtrl")

    driver.find_element_by_id("").click()  # 「加選課程」按鈕
    wait_for_url(driver, "")

    return


def course_taking(driver, course_ids):

    for course_id in course_ids:
        driver.find_element_by_id("").send_keys(course_id)
        driver.find_element_by_id("").click()  # 「序號直接加選」按鈕
        time.sleep(3 + 7 * random.random())
        response = driver.find_element_by_id("").text()



def main():
    try:    username, password, course_ids = read_account()
    except: return
    driver = selenium.webdriver.Chrome("chromedriver_win32\chromedriver.exe")
    login(driver, username, password)
    course_taking(driver, course_ids)
    driver.close()


""" Execution """
if __name__ == "__main__":
    main()