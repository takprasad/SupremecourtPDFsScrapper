from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from openpyxl import load_workbook
from pandas import ExcelWriter
import time
import os
import re
import csv
from datetime import datetime, timedelta
import calendar

#initialises the web driver
def initialize_Web_Driver(download_dir, url):
    options = webdriver.EdgeOptions()
    prefs = {
        "download.default_directory": download_dir,  # Set the download folder
        "download.prompt_for_download": False,       # Disable the download prompt
        "download.directory_upgrade": True,          # Auto-overwrite files
        "profile.default_content_setting_values.automatic_downloads": 1,  # Allow multiple downloads
        "plugins.always_open_pdf_externally": True,   # Avoid opening PDFs in the browser
        "safebrowsing.enabled": True 
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--log-level=3")
    options.add_argument("enable-automation")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")


    driver = webdriver.Edge(options=options)
    driver.maximize_window()


    #url = "https://digiscr.sci.gov.in/filtersearch"
    driver.get(url)

    # Wait for the page to load
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.ID, "doj3")))
    return driver


def create_csv(file_name):
    if os.path.exists(file_name):
        return
    columns = ['start_date','end_date','time_stamp','total_records','records_completed','completed']
    try:
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            
            writer.writerow(columns)
        
        print(f"CSV file '{file_name}' created successfully with only column names!")
    except Exception as e:
        print(f"An error occurred: {e}")
    
#checking date logs
def get_dates(start_date, end_date, file_path):
    start_date_obj = datetime.strptime(start_date, "%d-%m-%Y")
    end_date_obj = datetime.strptime(end_date, "%d-%m-%Y")

    
    
    df = pd.read_csv(file_path)    
    if not df.empty:
        last_row = df.iloc[-1]
        last_start_date = last_row["start_date"]
        last_end_date = last_row["end_date"]
    
        
        last_start_date_obj = datetime.strptime(last_start_date, "%d-%m-%Y")
        last_end_date_obj = datetime.strptime(last_end_date, "%d-%m-%Y")
        

        
            
        previous_month_start = (last_start_date_obj.replace(day=1) - timedelta(days=1)).replace(day=1)
        previous_month_end = (previous_month_start.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)

            
        return previous_month_start.strftime("%d-%m-%Y"), previous_month_end.strftime("%d-%m-%Y")
    
    return start_date, end_date

# writes into the logs
def write_into_log(start_date,end_date, file_path,n_records,comp,folder_path):
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)     
        file_names = os.listdir(folder_path)
        writer.writerow([start_date, end_date, current_timestamp,n_records,len(file_names),comp])
        
   
#set Download path
def set_donwload_path(driver, folder_name):
    """Downloads a PDF to the specified folder."""
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

   
    driver.command_executor._commands["setDownloadPath"] = (
        "POST", "/session/$sessionId/chromium/send_command"
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": folder_name},
    }
    driver.execute("setDownloadPath", params)

def get_number_of_records(driver):
    for i in range(3):
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="judgement-view"]/div[1]/div/div/div/div[1]/div[1]/div/span')))
            total_records = driver.find_element(By.XPATH,'//*[@id="judgement-view"]/div[1]/div/div/div/div[1]/div[1]/div/span')    
            return total_records.text.split(':')[-1]
        except:
            print("Exception in getting number of records")
    return 0
      
def next_page(driver,current_page_index):
        
        
    
        try:
            
            #The below xpath selects all the pagination buttons
            next_button = [page for page in driver.find_elements(By.XPATH, '//*[@id="judgement-view"]//ul/li/a') if page.text.strip() == str(current_page_index)]
           
            next_button = next_button[0]
            
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            
            
            time.sleep(1) 
            
            next_button.click()
            
            
            time.sleep(1) 
            return True
                 
              
        except :
            print("Could not get Next page by number")
        try:
            
            next_button = [page for page in driver.find_elements(By.XPATH, '//*[@id="judgement-view"]//ul/li/a') if page.text.strip() == "Next"]
            next_button = next_button[0]
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            time.sleep(1) 
            next_button.click()
            time.sleep(1) 
            return True
                    
                
        except :
            
            print(f"Completed {month} {year} !!")
            return False

def get_creation_time(item):
        item_path = os.path.join(folder_path, item)
        return os.path.getctime(item_path)

def delete_files(folder_path):
    
    files = os.listdir(folder_path)
    file_names = sorted(files, key=get_creation_time)
    
    k = len(file_names) % 15
    if k:
        for file in file_names[-k:]:
            os.remove(os.path.join(folder_path,file))
        print("Deleted files: "+str(k))      
 
 
def scrape_links(driver,current_page_index,output_path,failed_path):
    while True:
        if str(current_page_index) in checkpoint:
            current_page_index+=1
            time.sleep(1)
            if not next_page(driver,current_page_index):
                break
            continue  
        links = None
        for i in range(3):
            try:
                wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="judgement-view"]/div/div/div/div/div[3]/ul//li/div/div/div[1]/div/div[1]/div/a')))

                                                                    
                links = driver.find_elements(By.XPATH, '//*[@id="judgement-view"]/div/div/div/div/div[3]/ul//li/div/div/div[1]/div/div[1]/div/a') 
                links = [link.get_attribute('href') for link in links]
                break
            except:
                print("Problem in grabbing page links")
                
            
        
        if links:
                
            driver.switch_to.new_window('tab')
            
            if not download_pdfs(driver,links, current_page_index,output_path,failed_path):
                break
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        else:
            if current_page_index == 1:
                return False
            
        with open(checkpoint_file, "a") as f:
            f.write(str(current_page_index) + "\n")
        current_page_index +=1
        if not next_page(driver,current_page_index):
            break
    return True
        

def download_pdfs(driver,links,current_page_index,output_path,failed_path):
    
    pdf_links = []
    all_data = []
    clear = True
    for i in range(3):
        for link in links:
            try:
                if not isinstance(link, str):
                    link = str(link)
                driver.get(link) #This gets the page with meta-data
                time.sleep(1)                  
                name = driver.find_element(By.XPATH, "/html/body/div[1]/div/form/div[1]/div/h4").text
                rows = driver.find_elements(By.XPATH, "/html/body/div[1]/div/form/div[2]/div[1]/div/div[1]/div/div/div/table/tbody/tr")
                row_data = {}
                for row in rows:
                    columns = row.find_elements(By.TAG_NAME, "td")
                    if len(columns) >= 2:
                        title = columns[0].text.strip()
                        value = columns[1].text.strip()
                        row_data[title] = value
                row_data["Name"] = name
                all_data.append(row_data)
                try:
                    pdf = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[1]/a')
                    pdf_link = pdf.get_attribute('href')
                    pdf_links.append(pdf_link)
                    driver.get(pdf_link) 
                except:
                    pdf_link = None
                    pdf_links.append(pdf_link)
                    clear = False
                
                #Downloads the pdf file
                time.sleep(1)        
            except Exception as e:
                print(f"Error processing link {link}: {e}")
                break
        if not clear:
            delete_files(folder_path)
            break
    
        time.sleep(2)
        try:
            file_names = os.listdir(folder_path)
            
            
            if len(all_data) == 15 and len(file_names) % 15 != 0:
                delete_files(folder_path)
                continue
        except:
            print("Listdir error")
        
        file_names = sorted(file_names, key=get_creation_time)
        file_names = file_names[-len(all_data):]
        
        if(len(file_names) == len(all_data)):
            for idx in range(len(all_data)):
                #Simply extracts the Petitioner and Respondent as the filename call fname and does some formatting
                petitioner = all_data[idx]["Petitioner:"]
                respondent = all_data[idx]["Respondent:"]
                fname=  petitioner + " vs " + respondent 
                fname  =  re.sub(r'[^a-zA-Z0-9 ]', '', fname)
                fname = fname +".pdf"
                #print("Downloading File:",download_dir+"/"+file_names[idx])
                #print("Downloading as:",download_dir+"/"+fname)
                try:
                    
                    os.rename(os.path.join(folder_path,file_names[idx]), os.path.join(folder_path,fname))
                except:
                    
                    print("Renaming error!!!")
                all_data[idx]["File Name"]=fname
        else:
            print("Error: Length of file names is not the same as the rows in the report")
        #time.sleep(3)
        df_new = pd.DataFrame(all_data)
        output_file_path = f"{output_path}/output_{start_timestamp}.xlsx"
        
        if os.path.exists(output_file_path):
            df_existing = pd.read_excel(output_file_path)            
            if 'Sr No' not in df_existing.columns:
                df_existing.insert(0, 'Sr No', range(1, len(df_existing) + 1))            
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)           
            df_combined['Sr No'] = range(1, len(df_combined) + 1)            
            df_combined.to_excel(output_file_path, index=False)
            print(f"Data appended and saved to Excel file: {output_file_path}")
        else:           
            df_new.insert(0, 'Sr No', range(1, len(df_new) + 1)) 
            df_new.to_excel(output_file_path, index=False)
            print(f"New Excel file created and data saved: {output_file_path}")
        return True
    
    df_not = pd.DataFrame(all_data)
    df_not['Pdf_links'] = pdf_links
    page = [current_page_index for i in range(len(links))]
    df_not['Page'] = page
    failed_file_path = f"{failed_path}/Failed_downloads_{start_timestamp}.xlsx"
    
    if os.path.exists(failed_file_path):
        df_existing = pd.read_excel(failed_file_path)            
        if 'Sr No' not in df_existing.columns:
            df_existing.insert(0, 'Sr No', range(1, len(df_existing) + 1))            
        df_combined = pd.concat([df_existing, df_not], ignore_index=True)           
        df_combined['Sr No'] = range(1, len(df_combined) + 1)            
        df_combined.to_excel(failed_file_path, index=False)
        print(f"Data appended and saved to Excel file: {failed_file_path}")
    else:           
        df_not.insert(0, 'Sr No', range(1, len(df_not) + 1)) 
        df_not.to_excel(failed_file_path, index=False)
        print(f"New Excel file created and data saved: {failed_file_path}")
    return True
    
    
    
    
    
    
    

def check_completed(folder_path,total_records):
    file_names = os.listdir(folder_path)
    if file_names == None:
        return False
    if total_records == '':
        return False
    if len(file_names) == int(total_records):
        return True
    else:
        return False
        
    
     
     
if __name__ == "__main__":
    start_timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    
    
    url = "https://digiscr.sci.gov.in/filtersearch"
    
    download_dir = 'E:\job'    # Change this path as needed
    
    output_path = os.path.join(download_dir,'Outputs')
    failed_path = os.path.join(download_dir,'Failed_Downloads')
        
    if not os.path.exists(failed_path):
        os.makedirs(failed_path)
        
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    driver = initialize_Web_Driver(download_dir,url)
    
    date_log_file = os.path.join(download_dir,"Datelogs.csv")
    checkpoint_file =  os.path.join(download_dir,"Checkpoints.log")
    
    start_date = "01-03-2023"
    end_date =  "31-03-2023"
    
    create_csv(date_log_file)
    wait = WebDriverWait(driver, 20)
    while(True):
        start_date, end_date = get_dates(start_date,end_date,date_log_file)
        
        start_date_input = driver.find_element(By.ID, "doj3")
        end_date_input = driver.find_element(By.ID, "doj4")
        
        start_date_input.clear()
        end_date_input.clear()
        
        start_date_input.send_keys(start_date)
        end_date_input.send_keys(end_date)

        
        end_date_input.send_keys(Keys.TAB) #Sufficient to do the search
        button = driver.find_element(By.XPATH,'//*[@id="form-data"]/div[4]/div/div/div/div/button') 
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(1)  
        button.click()
        time.sleep(3)  
        
        day, month, year = start_date.split("-")
        month_name = calendar.month_name[int(month)] 
        
        folder_path = os.path.join(year, month_name)
        folder_path = os.path.join(download_dir,'Judgements',folder_path)
        set_donwload_path(driver,folder_path)
        n_records = get_number_of_records(driver)
        
        current_page = 1   
        checkpoint = open(checkpoint_file).read().strip() if os.path.exists(checkpoint_file) else "first"
        
        delete_files(folder_path)
        links = None
        
        
                
            
        if scrape_links(driver,current_page,output_path,failed_path):
            
            if check_completed(folder_path,n_records):
                comp = "Y"
            else:
                comp = "N"
            
            write_into_log(start_date,end_date,date_log_file,n_records,comp,folder_path)
        else:
            driver.refresh()
        with open(checkpoint_file, 'w') as file:
            pass
    driver.quit()
        
        
        
    
    
    
    