import glob
import shutil
import pandas as pd
import os
import time
import numpy as np
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Function to save the current state
def save_last_downloaded_indices(last_downloaded_indexa, last_downloaded_indexb):
    with open('last_downloaded_indices.txt', "w") as file:
        file.write(f"{last_downloaded_indexa}\n{last_downloaded_indexb}")
        
# Function to load the last donwloaded indices from file
def load_last_downloaded_indices():
    try:
        with open("last_downloaded_indices.txt", "r") as file: 
            lines = file.readlines()
            print(file)
            if len(lines) == 2:
                return int(lines[0]), int(lines[1])
            else:
                return 0, 0
    except FileNotFoundError:
       print("make appropriate .txt file")
       return 0, 0 # defaults indices to zero

# Journal title and publisher
def get_journal_and_pub(last_downloaded_indexb):
    journ_list = pd.read_excel(r'Journal Titles/Journal_list.xlsx')
    num_journals = journ_list.shape[0]
    journal_name = journ_list['Journal title'].iloc[last_downloaded_indexb]
    pub_name = journ_list['Publisher name'].iloc[last_downloaded_indexb]
    return num_journals, journal_name, pub_name

#function to find most recent file and its path
def most_recent_file():
    #transferring new file to folder with all files
    folder_path = r"/home/valentijn/Downloads"
    time.sleep(0.5)
    try:
        files_path = os.path.join(folder_path, '*')
        files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True) 
        file_name = files[0]
        actual_file_name = os.path.basename(file_name).split('/')[-1]
    except:
        time.sleep(1)
        files_path = os.path.join(folder_path, '*')
        files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True) 
        file_name = files[0]
        actual_file_name = os.path.basename(file_name).split('/')[-1]
    return file_name, actual_file_name

# Function to save most recent file to appropriate folder
def save_files_to_pub_folders(last_downloaded_indexa, last_downloaded_indexb, pub_title, journ_title, end_array_a):
    cased_title = pub_title.lower()          
    file_name, actual_file_name = most_recent_file()
    if "savedrec" in file_name:

        if 'elsevier' in cased_title:
            #Elsevier folder
            publisher = 'elsevier'
            new_folder_path = r'data/Elsevier/'
            
        elif 'wiley' in cased_title:
            #Wiley folder
            publisher = 'wiley'
            new_folder_path = r'data/Wiley/'
            
        elif "taylor" in cased_title:
            #Taylor and Francis folder
            publisher = 'taylor_francis'
            new_folder_path = r'data/Taylor_Francis/'
            
        elif 'springer' in cased_title:
            #Springer Nature folder
            publisher = 'springer'
            new_folder_path = r'data/Springer_Nature/'
            
        #convert index to string and move file to folder
        last_downloaded_indexa = str(last_downloaded_indexa)
        last_downloaded_indexb = str(last_downloaded_indexb)
        end_array_a = str(end_array_a)
        
        #new_file_path = new_folder_path + file_new + conv_indexa
        new_file_path = new_folder_path + publisher + "_row_" + last_downloaded_indexb + "_" + journ_title + "[" + last_downloaded_indexa + "of" + end_array_a + "]" + ".xls"
        print(new_file_path)
        shutil.move(file_name, new_file_path)
    else:
        print("tried to move invalid file, ensure files are moved manually before continuing")
last_downloaded_indexa, last_downloaded_indexb = load_last_downloaded_indices()

print(last_downloaded_indexa, last_downloaded_indexb)

# ... (your existing code)
#running in existing instance
#1 open cmd
#2 chdir C:\Program Files (x86)\Google\Chrome\Application
#3 chrome.exe -remote-debugging-port=9014 --user-data-dir="C:\Users\ben4f\Documents\Monash\FYP\Code\chrome_data"

executable='./chromedriver'
s=Service(executable)
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9014")

#Define function to run initial scrape
driver = webdriver.Chrome(options=chrome_options,service=s)
driver.get("https://go.openathens.net/redirector/www.monash.edu?url=https://www.webofscience.com/wos/woscc/basic-search")

#set base array value
array_0_val = 0
#publishers
#get amount of publishers
func_numtitles = get_journal_and_pub(last_downloaded_indexb)
numtitles = func_numtitles[0]

array_0_val_b = 0
#make array of that many numbers for loop to iterate through
array3 = np.arange(array_0_val_b,numtitles)
print(array3)

#begin while loop to iterate through publishers names
while last_downloaded_indexb < len(array3):
    try:
        #gatehring journal and publisher data
        driver.get('https://www.webofscience.com/wos/woscc/basic-search')
        time.sleep(2)
        journ_pub = get_journal_and_pub(last_downloaded_indexb)
        journ_title = journ_pub[1]
        pub_title = journ_pub[2]
        print(journ_title, pub_title)
        #waiting for webpage to load
        path_loading = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="snSearchType"]/div[1]/app-search-row/div/div[1]/app-select-search-field/wos-select/button')))
        
        #get url of loaded webpage
        url_initial = driver.current_url
        #selecting publication title
        xfieldchoice = driver.find_element(By.XPATH, '//*[@id="snSearchType"]/div[1]/app-search-row/div/div[1]/app-select-search-field/wos-select/button')
        xfieldchoice = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xfieldchoice))
        time.sleep(0.1)
        xfieldchoice.click()
        xfieldpubtitle = driver.find_element(By.XPATH, '//*[@id="global-select"]/div/div/div[5]/span')
        xfieldpubtitle = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xfieldpubtitle))
        time.sleep(0.1)
        xfieldpubtitle.click()

        #input journal title to field
        xjournalselect = driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-search-home/div[2]/div/app-input-route/app-search-basic/app-search-form/form/div[1]/app-search-row/div/div[2]/mat-form-field/div/div[1]/div[3]/input')
        xjournalselect = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xjournalselect))
        xjournalselect.clear()
        xjournalselect.send_keys(journ_title)
        time.sleep(0.1)
        xjournalselect.send_keys(Keys.RETURN)
        time.sleep(1)
        
        #gather url data
        url = driver.current_url
        if url == url_initial:
            last_downloaded_indexb = last_downloaded_indexb + 1
            save_last_downloaded_indices(last_downloaded_indexa, last_downloaded_indexb)

        else:
            #waiting for page to load
            path_loading = WebDriverWait(driver, 45).until(EC.presence_of_element_located((By.XPATH, '//*[@id="snRecListTop"]/app-export-menu/div/button/span[1]')))
            
            #capture amount of articles
            xnumberfull = driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-base-summary-component/app-search-friendly-display/div[1]/app-general-search-friendly-display/div/div[1]/h1/span')
            xnumtext = xnumberfull.text
            xnumtext = xnumtext.replace(",","")
            xnum = float(xnumtext)
            print(xnum)

            #make array for downloading 1000 each instance
            array1 = np.arange(array_0_val+1, xnum+1000,1000)
            array1len = len(array1)
            print('array1len = '+ str(array1len))
            array2 = np.arange(array_0_val, array1len, 1)
            print(array2)
            end_array_a = array2[-1]

            while last_downloaded_indexa < array1len - 1:
                try:
                    #bring up download dialogue box and select excel
                    #find lower data range value
                    minorval = array2[last_downloaded_indexa]
                    print(minorval)
                    minor = minorval*1000+1
                    print(minor)
                    conv_minor = str(minor)
                    #find higher data range value
                    major = array2[last_downloaded_indexa+1]*1000
                    print(major)
                    conv_major = str(major)
                    
                    #special error catching here as this is a common point of failure
                    error_val = 0
                    while error_val <= 2:
                        try:
                            #go back to search page
                            xtypebutton = driver.find_element(By.XPATH, '//*[@id="snRecListTop"]/app-export-menu/div/button[1]/span[1]')
                            xtypebutton = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xtypebutton))
                            time.sleep(0.5)
                            xtypebutton.click()
                            print('im in the first loop')
                            break
                        except KeyboardInterrupt:
                            print("you stopped the code")
                            error_val = 2
                            break
                        except BaseException as e:
                            time.sleep(1)
                            print(f'Unexpected error - retrying this portion of code')
                            error_val = error_val + 1
                            if error_val > 2:
                                print(f'Code was retried and still failed reccomend restarting code')
                                traceback.print_exc()
                                break

                    xexcel = driver.find_element(By.XPATH, '//*[@id="exportToExcelButton"]')
                    xexcel = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xexcel))
                    time.sleep(0.1)
                    xexcel.click()

                    #downloading full list greater 1000
                    #waiting for page to load
                    path_selector = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="radio3"]/label')))
                
                    xrecordvalue = driver.find_element(By.XPATH, '//*[@id="radio3"]/label')
                    xrecordvalue = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xrecordvalue))
                    time.sleep(0.1)
                    xrecordvalue.click()
                    
                    xvalueinputless = driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route[1]/app-export-overlay/div/div[3]/div[2]/app-export-out-details/div/div[2]/form/div/fieldset/mat-radio-group/div[3]/mat-form-field[1]/div/div[1]/div[3]/input')
                    xvalueinputless = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xvalueinputless))
                    xvalueinputless.clear()
                    xvalueinputless.send_keys(conv_minor)

                    xvalueinputmore = driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route[1]/app-export-overlay/div/div[3]/div[2]/app-export-out-details/div/div[2]/form/div/fieldset/mat-radio-group/div[3]/mat-form-field[2]/div/div[1]/div[3]/input')
                    xvalueinputmore = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xvalueinputmore))
                    xvalueinputmore.clear()
                    xvalueinputmore.send_keys(conv_major)

                    #downloading full list
                    xexceltype = driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route[1]/app-export-overlay/div/div[3]/div[2]/app-export-out-details/div/div[2]/form/div/div[1]/wos-select/button')
                    xexceltype = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xexceltype))
                    time.sleep(0.1)
                    xexceltype.click()
                    xexceltypeselect = driver.find_element(By.XPATH, '//*[@id="global-select"]/div/div/div[3]')
                    xexceltypeselect = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xexceltypeselect))
                    time.sleep(0.1)
                    xexceltypeselect.click()

                    xdwnrecord = driver.find_element(By.XPATH, '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route[1]/app-export-overlay/div/div[3]/div[2]/app-export-out-details/div/div[2]/form/div/div[2]/button[1]')
                    xdwnrecord = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xdwnrecord))
                    time.sleep(0.1)
                    xdwnrecord.click()

                    #wait until file downloaded to progress
                    down_files_name = "alpha"
                    while "savedrec" not in down_files_name and ".crdownload" not in down_files_name:
                        time.sleep(0.1)
                        file_name, down_files_name = most_recent_file()

                    save_files_to_pub_folders(last_downloaded_indexa, last_downloaded_indexb, pub_title, journ_title, end_array_a)
                    last_downloaded_indexa = last_downloaded_indexa+1

                    #error catching 
                except KeyboardInterrupt:
                    print("you stopped the code")
                    #error catching and saving most recent file to appropriate folder
                except BaseException as e:
                    print(f"An error occurred at journal index {last_downloaded_indexa}", e)
                    traceback.print_exc()
                    # Save the last downloaded indices in case of failure
                    save_last_downloaded_indices(last_downloaded_indexa, last_downloaded_indexb)
                    save_files_to_pub_folders(last_downloaded_indexa, last_downloaded_indexb, pub_title, journ_title, end_array_a)
                    break

            #special error catching here as this is a common point of failure
            error_val = 0
            while error_val <= 2:
                try:
                    #go back to search page
                    print('Moving back to the search page.')
#                    xbacktosearch = driver.find_element(By.XPATH, '//*[@id="breadcrumb"]/ul/li[1]/div/a/span/span')
#                    xbacktosearch = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(xbacktosearch))
#                    time.sleep(0.5)
#                    xbacktosearch.click()
                    driver.get('https://www.webofscience.com/wos/woscc/basic-search')
                    time.sleep(2)
                    print('im in the second loop')
                    break
                except KeyboardInterrupt:
                    print("you stopped the code")
                    error_val = 2
                    break
                except BaseException as e:
                    time.sleep(1)
                    print(f'Unexpected error - retrying this portion of code')
                    error_val = error_val + 1
                    if error_val > 2:
                        print(f'Code was retried and still failed reccomend restarting code')
                        traceback.print_exc()
                        break
            
            last_downloaded_indexa = 0
            last_downloaded_indexb = last_downloaded_indexb + 1
    except KeyboardInterrupt:
        print("you stopped the code")

    except BaseException as e:
        print(f"An error occurred at index {last_downloaded_indexb}", e)
        traceback.print_exc()
        # Save the last downloaded indices in case of failure
        save_last_downloaded_indices(last_downloaded_indexa, last_downloaded_indexb)
        save_files_to_pub_folders(last_downloaded_indexa, last_downloaded_indexb, pub_title, journ_title, end_array_a)
        break
    
# Save the state at the end of the program
save_last_downloaded_indices(last_downloaded_indexa, last_downloaded_indexb)

driver.quit()
