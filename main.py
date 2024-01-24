import requests
import time
import pyperclip
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
# noinspection PyPep8Naming
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from termcolor import cprint


METAMASK_EXT = 'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn'
XPATH_INPUT_UNLOCK = '//*[@data-testid="unlock-password"]'
XPATH_UNLOCK = '//*[@data-testid="unlock-submit"]'
XPATH_ONBOARDING_CREATE_NEW_WALLET = '//*[@data-testid="onboarding-create-wallet"]'
XPATH_IMPORT_WALLET = '//*[@data-testid="onboarding-import-wallet"]'
XPATH_AGREE = '//*[@data-testid="onboarding-terms-checkbox"]'
# XPATH_ONBOARDING_DONE = '//*[@data-testid="onboarding-complete-done"]'
XPATH_INPUTS_MNEMONIC = '//*[@class="MuiInputBase-input MuiInput-input"]'
XPATH_CONFIRM_MNEMONIC = '//*[@data-testid="import-srp-confirm"]'
XPATH_META_METRIX = '//*[@data-testid="metametrics-i-agree"]'
base_xpath = '//*[@data-testid="import-srp__srp-word-{}"]'  # Base XPath with placeholder
XPATH_CURRENCY_INPUT = '//*[@data-testid="network-form-ticker-input"]'
XPATH_INPUT_PASS = '//*[@data-testid="create-password-new"]'
XPATH_INPUT_PASS_CNFRM = '//*[@data-testid="create-password-confirm"]'
XPATH_INPUT_TERMS = '//*[@data-testid="create-password-terms"]'
XPATH_CREATE_NEW_WALLET = '//*[@data-testid="create-password-import"]'
XPATH_ONBOARDING_DONE = '//*[@data-testid="onboarding-complete-done"]'
XPATH_PIN_EXT_NEXT = '//*[@data-testid="pin-extension-next"]'
XPATH_PIN_EXT_DONE = '//*[@data-testid="pin-extension-done"]'
XPATH_POPOVER_CONTAINER = '//*[@class="popover-container"]'
XPATH_SUGGESTED_ID = '//*[@class="mm-box mm-text mm-button-base mm-button-link mm-button-link--size-auto mm-text--body-sm mm-box--padding-0 mm-box--padding-right-1 mm-box--padding-left-1 mm-box--display-inline-flex mm-box--justify-content-center mm-box--align-items-center mm-box--color-primary-default mm-box--background-color-transparent"]'

XPATH_NETWORKS = '/html/body/div[1]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div'
XPATH_POPUP_CLOSE = '//*[@class="popover-bg"]'

XPATH_CTA = '//*[@class="button btn--rounded btn-primary"]'
CSS_NETWORK_WRAPPER = '.new-network-info__wrapper button'
CSS_NETWORK_ERROR = '.networks-tab__add-network-form-body > div:nth-child(2).form-field__row--error'

NETWORKS = {
            'Holesky': {
                'net_name': 'Holesky',
                'rpc': 'https://ethereum-holesky.publicnode.com',
                'chain_id': 17000,
                'symbol': 'ETH',
                'explorer': 'https://holesky.etherscan.io/',
            },

            'Taiko': {
                'net_name': 'Taiko Katla L2',
                'rpc': 'https://taiko-katla.blockpi.network/v1/rpc/public',
                'chain_id': 167008,
                'symbol': 'ETH',
                'explorer': 'https://explorer.katla.taiko.xyz',
            },

            'BSC': {
                'net_name': 'Smart Chain',
                'rpc': 'https://bsc-dataseed.binance.org/',
                'chain_id': 56,
                'symbol': 'BNB',
                'explorer': 'https://bscscan.com',
            },

            'Polygon': {
                'net_name': 'Polygon',
                'rpc': 'https://polygon-rpc.com',
                'chain_id': 137,
                'symbol': 'MATIC',
                'explorer': 'https://polygonscan.com/',
            },
        }


def get_driver(zero, ads_id):
    try:
        open_url = "http://local.adspower.net:50325/api/v1/browser/start?user_id=" + ads_id

        resp = requests.get(open_url).json()

        chrome_driver = resp["data"]["webdriver"]
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
        chrome_service = Service(executable_path=chrome_driver)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        return driver
    except Exception:
        cprint(f'{zero + 1}. {ads_id}: error during driver init', 'yellow')
        raise  # This line will re-raise the exception


def click(driver, xpath, wait=5):
    try:
        WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.find_element(By.XPATH, xpath).click()
    except Exception:
        cprint(f'error while try to click xpath {xpath}', 'yellow')
        raise  # This line will re-raise the exception


def search(driver, by, selector, wait=5):
    # noinspection PyBroadException
    try:
        WebDriverWait(driver, wait).until(EC.presence_of_element_located((by, selector)))
        return True
    except Exception:
        return False


def paste(driver, text, xpath):
    try:
        current_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        current_field.send_keys(text)  # Send
        # pyperclip.copy(text)
        # ActionChains(driver).key_down(u'\ue03d').send_keys('v').perform()
    except Exception:
        cprint(f'error while try paste ${text}', 'yellow')
        raise  # This line will re-raise the exception

def add_network(driver, name_network):
    cprint(f'add network flow {name_network}', 'white')

    try:
        # Navigate to the add network page
        driver.get(f'{METAMASK_EXT}/home.html#settings/networks/add-network')

        # Close any popup if present
        if search(driver, By.CSS_SELECTOR, CSS_NETWORK_WRAPPER, 2):
            driver.find_element(By.CSS_SELECTOR, CSS_NETWORK_WRAPPER).click()

        # Network Name
        click(driver, "//h6[contains(text(), 'Ім’я мережі')]/ancestor::label//input")
        paste(driver, NETWORKS[name_network]['net_name'], "//h6[contains(text(), 'Ім’я мережі')]/ancestor::label//input")

        # New RPC URL
        click(driver,  "//h6[contains(text(), 'Новий RPC URL')]/ancestor::label//input")
        paste(driver, NETWORKS[name_network]['rpc'],  "//h6[contains(text(), 'Новий RPC URL')]/ancestor::label//input")

        # Chain ID
        click(driver,  "//h6[contains(text(), 'ID мережі')]/ancestor::label//input")
        paste(driver, NETWORKS[name_network]['chain_id'],  "//h6[contains(text(), 'ID мережі')]/ancestor::label//input")

        # Currency Symbol
        
        click(driver,  XPATH_SUGGESTED_ID)
        # EXPLORER
        click(driver,  "//h6[contains(text(), 'Блокувати Explorer')]/ancestor::label//input")
        paste(driver, NETWORKS[name_network]['explorer'],  "//h6[contains(text(), 'Блокувати Explorer')]/ancestor::label//input")
        # paste(driver, NETWORKS[name_network]['symbol'],  XPATH_CURRENCY_INPUT)
        time.sleep(1)

        # Click Save button
        click(driver, XPATH_CTA)
        time.sleep(1)

        # Confirm network switch, if prompted
        click(driver, XPATH_CTA, 2)

        time.sleep(2)

    except Exception as e:
        cprint(f'⚠️ adding network < {name_network} > with an error: {str(e)}', 'red')
        traceback.print_exc()

# def add_network(driver, name_network):
#     cprint(f'add network flow {name_network}', 'white')
#     # noinspection PyBroadException
#     try:
#         driver.get(f'{METAMASK_EXT}/home.html#settings/networks/add-network')

#         if search(driver, By.CSS_SELECTOR, CSS_NETWORK_WRAPPER, 2):  # close popup that some network is added
#             driver.find_element(By.CSS_SELECTOR, CSS_NETWORK_WRAPPER).click()

#         click(driver, f'{XPATH_NETWORKS}[1]/label/input')        # CLICK input Network name
#         paste(driver, NETWORKS[name_network]['net_name'], f'{XPATH_NETWORKS}[1]/label/input')        # PASTE 'net_name'
#         click(driver, f'{XPATH_NETWORKS}[2]/label/input', 0)     # CLICK input New RPC URL
#         paste(driver, NETWORKS[name_network]['rpc'], f'{XPATH_NETWORKS}[2]/label/input')             # PASTE 'rpc'
#         click(driver, f'{XPATH_NETWORKS}[3]/label/input', 0)     # CLICK input Chain ID
#         paste(driver, NETWORKS[name_network]['chain_id'], f'{XPATH_NETWORKS}[3]/label/input')        # PASTE 'chain_id'
#         click(driver, f'{XPATH_NETWORKS}[4]/label/input', 0)     # CLICK input Currency symbol
#         paste(driver, NETWORKS[name_network]['symbol'], f'{XPATH_NETWORKS}[4]/label/input')          # PASTE 'symbol'
#         click(driver, f'{XPATH_NETWORKS}[5]/label/input', 0)     # CLICK input Block explorer URL (Optional)
#         paste(driver, NETWORKS[name_network]['explorer'], f'{XPATH_NETWORKS}[5]/label/input')        # PASTE 'explorer'
#         time.sleep(1)                                            # WAIT 1 second
#         if search(driver, By.CSS_SELECTOR, CSS_NETWORK_ERROR, 0):
#             cprint(f'⚠️ adding network < {name_network} > - looks like added', 'yellow')
#         else:
#             click(driver, XPATH_CTA, 0)                          # CLICK button "Save"
#             click(driver, XPATH_CTA)                             # CLICK button "Got it" - You have switched to
#             time.sleep(2)
#     except Exception:
#         cprint(f'⚠️ adding network < {name_network} > with an error', 'red')
#         traceback.print_exc()  # This line will print the exception stacktrace

# def input_seed_phrase(driver, xpath, seed):
#     words = seed.split()  # Split the seed phrase into individual words
#     if len(words) != 12:
#         raise ValueError("The seed phrase does not contain 12 words.")

#     for word in words:
#         current_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
#         current_field.send_keys(word)  # Send the word to the input field
#         time.sleep(0.5)  # Short delay to allow UI to update
#         current_field.send_keys(Keys.TAB)  # First Tab press
#         time.sleep(0.5)  # Short delay to allow UI to update
#         current_field.send_keys(Keys.TAB)  # Second Tab press
#         time.sleep(0.5)  # Short delay for safety

#         # Update the xpath to point to the next input field, if necessary
#         # xpath = ... (update if necessary)
        
def input_seed_phrase(driver, base_xpath, seed):
    words = seed.split()  # Split the seed phrase into individual words
    if len(words) != 12:
        raise ValueError("The seed phrase does not contain 12 words.")

    for index, word in enumerate(words):
        # Construct the XPath for the current input field
        xpath = base_xpath.format(index)
        current_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        current_field.send_keys(word)  # Send the word to the input field
        if index < 11:  # No need to tab on the last word
            # current_field.send_keys(Keys.TAB)  # First Tab press
            # time.sleep(0.5)  # Short delay to allow UI to update
            # current_field.send_keys(Keys.TAB)  # Second Tab press
            time.sleep(0.5)  # Short delay for safety


def onboard(driver, seed, password):
    time.sleep(10)                                            # WAIT 1 second
    try:
        click(driver, XPATH_AGREE)               # CLICK button "Agree"
        click(driver, XPATH_IMPORT_WALLET)       # CLICK button "Import an existing wallet"
        click(driver, XPATH_META_METRIX)         # CLICK XPATH_META_METRIX
        click(driver, base_xpath.format(0))  # Click on the first input field to ensure focus
        input_seed_phrase(driver, base_xpath, seed)
        # click(driver, XPATH_INPUTS_MNEMONIC)     # CLICK input for mnemonic (first one)
        # input_seed_phrase(driver, XPATH_INPUTS_MNEMONIC, seed)  
        # paste(driver, seed)                      # PASTE 'mnemonic'
        click(driver, XPATH_CONFIRM_MNEMONIC)    # CLICK button "Confirm Secret Recovery Phrase"
        click(driver, XPATH_INPUT_PASS)          # CLICK input "New password (8 characters min)"
        paste(driver, password, XPATH_INPUT_PASS)                  # PASTE 'password'
        click(driver, XPATH_INPUT_PASS_CNFRM)    # CLICK input "Confirm password"
        paste(driver, password, XPATH_INPUT_PASS_CNFRM)                  # PASTE 'password'
        click(driver, XPATH_INPUT_TERMS)         # CLICK checkbox "I understand that MetaMask cannot ..."
        click(driver, XPATH_CREATE_NEW_WALLET)   # CLICK button "Create a new wallet"
        click(driver, XPATH_ONBOARDING_DONE)     # CLICK button "Got it!"
        click(driver, XPATH_PIN_EXT_NEXT)        # CLICK button "Next"
        click(driver, XPATH_PIN_EXT_DONE)        # CLICK button "Done"
    except Exception:
        cprint(f'❌ error during MetaMask onboarding flow', 'yellow')
        raise  # This line will re-raise the exception


def unlock(driver, password):
    try:
        print('unlock flow')
        click(driver, XPATH_INPUT_UNLOCK)    # CLICK input "password"
        paste(driver, password, XPATH_INPUT_UNLOCK)              # PASTE 'password'
        print('click unlock', password)
        click(driver, XPATH_UNLOCK)          # CLICK input "Unlock"
        if search(driver, By.XPATH, XPATH_ONBOARDING_DONE):  # IMPORT SEED IF FIRST RUN OF METAMASK
            print('found unlocl')
            click(driver, XPATH_ONBOARDING_DONE)     # CLICK button "Done"
        if search(driver, By.XPATH, XPATH_PIN_EXT_NEXT):  # UNLOCK METAMASK WITH PASSWORD IF ALREADY EXIST
            click(driver, XPATH_PIN_EXT_NEXT)         # CLICK button "Done"
        if search(driver, By.XPATH, XPATH_PIN_EXT_DONE):       # UNLOCK METAMASK WITH PASSWORD IF ALREADY EXIST
            click(driver, XPATH_PIN_EXT_DONE)
        if search(driver, By.XPATH, XPATH_POPUP_CLOSE):
            click(driver, XPATH_POPUP_CLOSE)
        
    except Exception:
        cprint(f'❌ error during MetaMask unlock flow', 'yellow')
        raise  # This line will re-raise the exception


def main(zero, ads_id, seed, password):
    close_url = "http://local.adspower.net:50325/api/v1/browser/stop?user_id=" + ads_id
    driver = None
    try:
        driver = get_driver(zero, ads_id)

        driver.get(f'{METAMASK_EXT}/home.html')            # Open MetaMask plugin, should be already installed

        if search(driver, By.XPATH, XPATH_IMPORT_WALLET):  # IMPORT SEED IF FIRST RUN OF METAMASK
            cprint(f'🆕 {zero + 1}. {ads_id}: onboard flow', 'white')
            onboard(driver, seed, password)
        elif search(driver, By.XPATH, XPATH_UNLOCK):       # UNLOCK METAMASK WITH PASSWORD IF ALREADY EXIST
            cprint(f'🔑 {zero + 1}. {ads_id}: unlock flow', 'white')
            unlock(driver, password)
        else:
            raise NoSuchElementException(f"❌ Element with xpath '{XPATH_IMPORT_WALLET}' "
                                         f"and '{XPATH_UNLOCK}' not found.")

        # ============================= if you don't need to add a networks, delete everything below ===================
        time.sleep(2)
        # add_network(driver, 'Holesky')
        add_network(driver, 'Taiko')
        # add_network(driver, 'Optimism')
        # add_network(driver, 'Arbitrum')
        # ==============================================================================================================

        driver.quit()
        requests.get(close_url)

        cprint(f'✅ {zero + 1}. {ads_id} = done', 'green')

    except Exception:
        cprint(f'❌ {zero + 1}. {ads_id}: error happens 🤷🏻', 'yellow')
        driver.quit()
        requests.get(close_url)
        raise  # This line will re-raise the exception


with open("id_users.txt", "r") as f:
    id_users = [row.strip() for row in f]

with open("seeds.txt", "r") as f:
    seeds = [row.strip() for row in f]

password_metamask = 'Aura1234!'  # password for metamask

for i, adspower_id in enumerate(id_users):
    main(i, adspower_id, seeds[i], password_metamask)
