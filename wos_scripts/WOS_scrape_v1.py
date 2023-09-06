# Set up code space and import/start required drivers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


# Define function to run initial scrape
driver = webdriver.Chrome()
driver.get("https://go.openathens.net/redirector/www.monash.edu?url=https://www.webofscience.com/wos/woscc/basic-search")
# driver.get("https://go.openathens.net/redirector/www.monash.edu\?url=https%3A%2F%2Fwww.webofknowledge.com%2F%3FDestApp%3DWOS")

# log into monash OKTA
time.sleep(2)

urname = 'czub0002@student.monash.edu'
pword = 'IvoKarlovicACE'

xgrabuser = driver.find_element(By.XPATH, '//*[@id="okta-signin-username"]')
xgrabuser.send_keys(urname)

xgrabpwrd = driver.find_element(By.XPATH, '//*[@id="okta-signin-password"]')
xgrabpwrd.send_keys(pword)

xlogin = driver.find_element(By.XPATH, '//*[@id="okta-signin-submit"]')
xlogin.click()
time.sleep(5)
xsendpush = driver.find_element(By.XPATH,'//*[@id="okta-sign-in"]/div[2]/div/div/span[1]/div/label')
xsendpush.click()

xdntchalnge = driver.find_element(By.XPATH, '//*[@id="okta-sign-in"]/div[2]/div/div/span[2]/div/label')
xdntchalnge.click()

time.sleep(2)
xoktapush = driver.find_element(By.XPATH, '//*[@id="form66"]/div[2]/input')
xoktapush.click()

time.sleep(40)

#getting past cookies to access website
cookieclear = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
cookieclear.click()

#selecting publication title
xfieldchoice = driver.find_element(By.XPATH, '//*[@id="snSearchType"]/div[1]/app-search-row/div/div[1]/app-select-search-field/wos-select/button')
xfieldchoice.click()

xfieldpubtitle = driver.find_element(By.XPATH, '//*[@id="global-select"]/div[1]/div/div[5]/span')
xfieldpubtitle.click()

#journals
J1 = 'Journal of Water Resources'
J2 = 'Journal of Hydrology'

#years
Y1 = '2022'
#enter journal title
xjournalselect = driver.find_element(By.XPATH, '//*[@id="mat-input-0"]')
xjournalselect.send_keys(J2)

#Add dates
xadddate = driver.find_element(By.XPATH, '//*[@id="snSearchType"]/div[2]/button[2]/span[1]')



driver.quit()