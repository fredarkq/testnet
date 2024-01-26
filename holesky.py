import requests
import time
import pyperclip
import traceback
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from termcolor import cprint
import openpyxl


XPATH_INPUT = '//*[@class="form-control"]'
XPATH_BUTTON_START = '//*[@class="btn btn-success start-action"]'
XPATH_MODAL = '//*[@class="modal-content"]'
XPATH_MODAL_CLOSE = '//*[@aria-label="Close"]'
XPATH_CAPTCHA = '//*[@class="ctp-checkbox-label"]'
XPATH_CAPTCHA_DONE = '//*[@class="success-circle"]'
XPATH_ALERT_DANGER = '//div[@class="alert alert-danger"]'
XPATH_MINNING = '//div[@class="col pow-status-image"]'

def click(driver, xpath, wait=5):
    try:
        WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.find_element(By.XPATH, xpath).click()
    except Exception:
        cprint(f'error while try to click xpath {xpath}', 'yellow')
        raise  # This line will re-raise the exception


def paste(driver, text, xpath):
    try:
        current_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        current_field.send_keys(text)  # Send
        # pyperclip.copy(text)
        # ActionChains(driver).key_down(u'\ue03d').send_keys('v').perform()
    except Exception:
        cprint(f'error while try paste ${text}', 'yellow')
        raise  # This line will re-raise the exception

def close_tabs_except_current(driver, target_url):
    # Get the current window handle
    current_window = driver.current_window_handle

    # Get all window handles
    all_windows = driver.window_handles

    # Close tabs/windows except the current one
    for window in all_windows:
        if window != current_window:
            driver.switch_to.window(window)
            driver.close()

    # Switch back to the original window
    driver.switch_to.window(current_window)

    # Ensure that the target URL is loaded in the current window
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_to_be(target_url))

def search(driver, by, selector, wait=5):
    # noinspection PyBroadException
    try:
        WebDriverWait(driver, wait).until(EC.presence_of_element_located((by, selector)))
        return True
    except Exception:
        return False

def find_and_close_modal(driver, xpath):
    try:
        # Replace XPATH_MODAL with the actual XPath for your modal element
        current_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        # Check if the modal is visible
        if current_field.is_displayed():
            time.sleep(random.uniform(1, 5))
            text = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_ALERT_DANGER))).text
            cprint(f'{text}', 'red')

            time.sleep(random.uniform(1, 3))
            close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, XPATH_MODAL_CLOSE)))
            close_button.click()
            time.sleep(random.uniform(1, 5))
            return True
        else:
            print("Modal is not visible")
            return False

    except Exception as e:
        print(f'Error while trying to find and close modal: {str(e)}')
        # Optionally, you can choose to re-raise the exception
        # raise

def captcha(driver, wallet):
      try:
           click(driver, XPATH_BUTTON_START, 10)
           time.sleep(random.uniform(1, 5))
           error = find_and_close_modal(driver, XPATH_MODAL)

           if  error:
               print('found XPATH_CAPTCHA_DONE')
               click(driver, XPATH_INPUT)
               time.sleep(random.uniform(3, 5))
               paste(driver, wallet, XPATH_INPUT)
               time.sleep(random.uniform(4, 7))
               click(driver, XPATH_BUTTON_START, 10)
               time.sleep(random.uniform(1, 5))
               current_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, XPATH_MINNING)))

           else:
                print("Modal is not visible")

      except TimeoutException: # Open a new tab
            time.sleep(2)
#             driver.switch_to.window(driver.window_handles[1])  # Switch to the new tab
            driver.get(f'https://holesky-faucet.pk910.de/')


            time.sleep(random.uniform(5, 10))
            captcha(driver, wallet)


def holeskyC(driver, wallet):
   cprint(f'❌ {driver } ', 'blue')
   cprint(f'❌ {wallet } ', 'blue')
   driver.get(f'https://holesky-faucet.pk910.de/')
#    close_tabs_except_current(driver, 'https://holesky-faucet.pk910.de/')
   time.sleep(random.uniform(5, 10))
   captcha(driver, wallet )


   if search(driver, By.XPATH, XPATH_CAPTCHA_DONE):  # IMPORT SEED IF FIRST RUN OF METAMASK
       print('found XPATH_CAPTCHA_DONE')
       click(driver, XPATH_INPUT)
       time.sleep(random.uniform(1, 5))
       paste(driver, wallet, XPATH_INPUT)
       click(driver, XPATH_BUTTON_START, 10)
   else:
        driver.refresh()
        time.sleep(random.uniform(5, 10))



