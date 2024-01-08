import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from time import sleep

# Set up logging to capture ERROR, WARNING, INFO, and DEBUG messages
logging.basicConfig(
    filename='selenium_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

username = 'username' # username
password = 'password' # password

# Initialize Chrome WebDriver
try:
    driver = webdriver.Chrome()
except Exception as e:
    logging.error(f"An error occurred: {e}")
# Replace 'your_website_url' with the URL of the website
website_url = 'https://www.way2drug.com/PASSOnline/'

def main():
    try:
        # Open the website
        driver.get(website_url)

        # Find and click the button that triggers the pop-up window
        trigger_button = driver.find_element(By.CSS_SELECTOR, "#registration img")
        trigger_button.click()

        popup_division = driver.find_element(By.ID, 'fancybox-inner')
        username_field = popup_division.find_element(By.NAME, 'user_login')
        password_field = popup_division.find_element(By.NAME, 'user_password')
        login_button_in_popup = popup_division.find_element(By.ID, 'register')

        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        login_button_in_popup.click()

        # # Initialize an empty DataFrame to store results
        # result_df = pd.DataFrame(columns=["SMILES", "Result"])

        # Read SMILES from an Excel file
        # df = pd.read_excel('4628_inputs.xlsx')
        # smiles_list = df['SMILES'].to_list()

        input_file = open('input_smiles.txt','r')
        smiles_list = input_file.readlines()
        smiles_list = [smiles.strip() for smiles in smiles_list]
        

        driver.find_element(By.ID, "myHeader1").click()
        driver.find_element(By.ID, "smiles").click()

        for idx,smile in enumerate(smiles_list):
            # Click on elements and perform operations for each SMILES
            # logging.error(f'input {idx} : {smile}')

            driver.find_element(By.ID, "smi").click()
            driver.find_element(By.ID, "smi").clear()
            driver.find_element(By.ID, "smi").send_keys(smile)
            driver.find_element(By.CSS_SELECTOR, "#myContent4 input:nth-child(4)").click()
            # logging.error("Results produced\n")
            wait = WebDriverWait(driver, 10)
            click2_element = wait.until(EC.element_to_be_clickable((By.ID, "click2")))
            actions = ActionChains(driver)
            actions.move_to_element(click2_element).perform()
            
            # Click the "click2" element
            click2_element.click()
            # logging.error("Clicked 2")

            iframe_element1 = driver.find_element(By.XPATH, "//iframe[@id='results1']")
            driver.switch_to.frame(iframe_element1)

            # Waiting for the tables in the first iframe to load (you may need to adjust the wait time)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

            # Obtaining the HTML source of the first iframe
            iframe1_html = driver.page_source

            # Using pandas to read tables from the first iframe's HTML source
            tables1 = pd.read_html(iframe1_html)

            # Assuming you have only one table in the first iframe, you can access it as follows:
            if len(tables1) > 0:
                result_table1 = tables1[0]
            else:
                logging.error("No Tables in iframe 1")
                # Now you can work with the result_table1 DataFrame as needed
            cols=list(result_table1.columns)

            result_table1.columns=['Pa','Pi','Activity']
            # result_table1 = result_table1[result_table1['Pa'] > 700]

            result_table1['Pa']=result_table1['Pa']/1000
            result_table1['Pi']=result_table1['Pi']/1000

            # Reset the index if needed
            result_table1 = result_table1.reset_index(drop=True)
            result_table1['SMILES']=smile
            # logging.error('table 1')
            # Switch back to the main content
            driver.switch_to.default_content()

            # Switch to the second iframe (results2) using XPath
            iframe_element2 = driver.find_element(By.XPATH, "//iframe[@id='results2']")
            driver.switch_to.frame(iframe_element2)

            # Wait for the tables in the second iframe to load (you may need to adjust the wait time)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

            # Obtain the HTML source of the second iframe
            iframe2_html = driver.page_source

            # Using pandas to read tables from the second iframe's HTML source
            tables2 = pd.read_html(iframe2_html)

            # Making s you have only one table in the second iframe, you can access it as follows:
            if len(tables2) > 0:
                result_table2 = tables2[0]
                # Now you can work with the result_table2 DataFrame as needed
            
            result_table2.columns=['Pa','Pi','Activity']
            #result_table2 = result_table2[result_table2['Pa'] > 700]

            result_table2['Pa']=result_table2['Pa']/1000
            result_table2['Pi']=result_table2['Pi']/1000

            # Reset the index if needed
            result_table1 = result_table1.reset_index(drop=True)
            result_table2['SMILES']=smile
            # logging.error('table 2')
            # Switch back to the main content
            driver.switch_to.default_content()

            result_table1=result_table1[['SMILES','Pa','Pi','Activity']]
            result_table2=result_table2[['SMILES','Pa','Pi','Activity']]

            if idx == 0:
                result_table1[1:].to_csv("Biological Activity.txt",sep='\t',index=False,mode='a')
                result_table2[1:].to_csv("Toxicity.txt",sep='\t',index=False,mode='a')
            else:
                result_table1[1:].to_csv("Biological Activity.txt",sep='\t',index=False,mode='a',header=False)
                result_table2[1:].to_csv("Toxicity.txt",sep='\t',index=False,mode='a',header=False)

            sleep(3)
            logging.info(f'{idx} {smile} done')
            # idx=idx+1
        logging.info("all done")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        driver.quit()

if __name__ == '__main__':
    main()
