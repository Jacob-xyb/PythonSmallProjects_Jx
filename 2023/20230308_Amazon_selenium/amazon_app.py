from selenium import webdriver
from selenium.webdriver.common.by import By
import time

import amazon_tool

# "C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe" -remote-debugging-port=9014 --user-data-dir="C:\\Users\\Administrator\AppData\Local\Google\Chrome\\User Data"


# "C:\Program Files\Google\Chrome\Application\chrome.exe" -remote-debugging-port=9014 --user-data-dir="C:\\Users\\mac\AppData\Local\Google\Chrome\\User Data"

# region USER_API
EXCEL_NAME = "采集录入 (2).xlsx"
SHEET_NAME = "模板"
WAIT_TIME = {
    "wait_plugin_load": 10,
}


# endregion


def get_download_btn(driver):
    dialog = driver.find_element(By.XPATH, f'//*[@id="content-ext-main"]/div/div[6]/div')
    # print(dialog)
    return dialog.find_elements(
        By.CSS_SELECTOR,
        f'a > svg > use')


def get_first_rowID(driver):
    tbdoy = driver.find_element(
        By.XPATH,
        f'//*[@id="content-ext-main"]/div/div[3]/div/div[2]/div[1]/div[2]/table/tbody/tr'
    )
    return tbdoy.get_attribute("rowid")


def get_item_btn(driver, index):
    tbdoy = driver.find_element(
        By.XPATH,
        f'//*[@id="content-ext-main"]/div/div[3]/div/div[2]/div[1]/div[2]/table/tbody'
    )
    return tbdoy.find_elements(By.CSS_SELECTOR, f"tr[rowid=row_{index + 1}] > td:nth-child(14) span")


def get_max_rows(driver):
    flag = True
    count = 0
    span = []
    while flag and count < 10:
        span = driver.find_elements(
            By.XPATH,
            f'//*[@id="content-ext-main"]/div/footer/div/div[2]/span[1]'
        )
        if span and len(span[0].text.split()) == 3:
            flag = False
        else:
            count += 1
            time.sleep(3)

    return int(span[0].text.split()[1])


def get_btn_Close(driver):
    return driver.find_element(
        By.XPATH,
        f"/html/body/div[2]/div[2]/div[2]/header/div/div/div[5]/svg"
    )


def get_btn_LoadMore(driver):
    return driver.find_element(
        By.XPATH,
        f"/html/body/div[2]/div[2]/div[2]/main/div/footer/div/div[2]/span[2]/div"
    )


def get_btn_MonthlySales(driver):
    return driver.find_element(
        By.XPATH,
        f'//*[@id="content-ext-main"]/div/div[6]/div/div[1]/div[1]/ul/li[2]'
    )


def run_single_case(wd, case):
    start_page = int(case["start"])
    max_page = int(case["end"])
    for page in range(start_page, max_page + 1):
        run_single_page(wd, case, page)


def click_btn_plugin(driver):
    flag = True
    count = 0
    btn = []
    while flag and count < 5:
        btn = driver.find_elements(
            By.XPATH,
            f'//*[@id="main-sellersprite-extension"]/div[4]'
        )
        if btn:
            flag = False
        else:
            count += 1
            time.sleep(3)

    btn[0].click()


def click_btn_download(driver):
    while True:
        btn = get_download_btn(driver)
        # print(btn, len(btn))
        if btn:
            btn[0].click()
            break
        time.sleep(1)


def run_single_page(wd, case, page):
    wd.get(case['url'].format(page))
    # open plugin
    click_btn_plugin(wd)
    time.sleep(WAIT_TIME["wait_plugin_load"])

    # get_btn_Close(wd).click()
    # time.sleep(1)
    # Load_More(wd, int(case["end"]))
    crt_item = get_first_rowID(wd).split('_')[-1]
    crt_item = int(crt_item) - 1
    # for i in range(3):
    for i in range(get_max_rows(wd)):
        item_btn = get_item_btn(wd, crt_item)
        # wd.execute_script("arguments[0].focus();", item_btn)
        # item_btn.send_keys("{DOWN}")

        if item_btn:
            item_btn[0].click()
            time.sleep(2)

            click_btn_download(wd)
            time.sleep(1)
            # 月销量
            get_btn_MonthlySales(wd).click()
            time.sleep(1)
            click_btn_download(wd)
            time.sleep(1)
            # 月销量
            get_btn_MonthlySales(wd).click()
            time.sleep(1)
            # 退出弹窗
            wd.find_element(By.XPATH, f'//*[@id="content-ext-main"]/div/div[6]/div/div[1]/div[2]').click()
            time.sleep(1)

        div = wd.find_element(By.XPATH, f'//*[@id="content-ext-main"]/div/div[3]/div/div[2]/div[1]/div[2]')
        wd.execute_script("arguments[0].scrollBy(0, 48)", div)
        crt_item += 1
        time.sleep(3)


# region # 暂时不用的函数
def get_item_QA(driver, index):
    tbdoy = driver.find_element(
        By.XPATH,
        f"/html/body/div[2]/div/div[2]/main/div/div[2]/div[3]/div[2]/div[1]/div[2]/table/tbody"
    )
    return tbdoy.find_element(By.CSS_SELECTOR, f"tr[rowid=row_{index + 1}] > td:nth-child(13) span")


def get_btn_NextPage(driver):
    return driver.find_element(
        By.CSS_SELECTOR,
        f"div.a-cardui._cDEzb_card_1L-Yx > div.a-text-center > ul > li.a-last"
    )


def click_NextPage(driver):
    btn_NextPage = get_btn_NextPage(wd)
    driver.execute_script("arguments[0].scrollIntoView();", btn_NextPage)
    btn_NextPage.click()
    time.sleep(5)


def Load_More(driver, num):
    wait_time = 30
    crt_max_row = get_max_rows(driver)
    crt_time = time.time()
    now_max_row = crt_max_row
    for i in range(num - 1):
        get_btn_LoadMore(driver).click()
        while now_max_row == crt_max_row:
            time.sleep(3)
            now_time = time.time()
            now_max_row = get_max_rows(driver)
        crt_max_row = now_max_row


# endregion


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()

    # chrome_options.add_argument("--user-data-dir=" + r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data")

    # "C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe" -remote-debugging-port=9014 --user-data-dir="C:\\Users\\Administrator\AppData\Local\Google\Chrome\\User Data"
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9014")

    wd = webdriver.Chrome(options=chrome_options)
    wd.implicitly_wait(5)
    wd.minimize_window()
    wd.maximize_window()

    case_list = amazon_tool.get_cases(EXCEL_NAME, SHEET_NAME)

    for case in case_list:
        run_single_case(wd, case)
    input()
