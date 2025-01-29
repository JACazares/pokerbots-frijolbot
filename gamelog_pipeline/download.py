from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def scrape_with_selenium():
    # 1. Set up the WebDriver (Chrome, for example)
    driver = webdriver.Chrome()
    
    # Use a dictionary to keep counters for repeated (challenger, opponent, bot)
    counters = {}

    driver.get(f"https://scrimmage.pokerbots.org/")
    # Wait for the user to manually log in
    input("Please log in manually and then press Enter to continue...")
    
    for page_num in range(2, 23):
        # 2. Navigate to the page that has your game list
        driver.get(f"https://scrimmage.pokerbots.org/team/games?page={page_num}")
        time.sleep(2)
        
        # -- If you need to log in manually, do it here --
        # For example:
        #   username_field = driver.find_element(By.ID, "username")
        #   password_field = driver.find_element(By.ID, "password")
        #   login_button   = driver.find_element(By.ID, "login-button")
        #   username_field.send_keys("your_username")
        #   password_field.send_keys("your_password")
        #   login_button.click()
        #
        # Or use your own login logic. If your browser session is already logged in,
        # you might reuse that profile or just do the manual step in the automated browser.
        
        # 3. Wait for the table to load (adjust the wait time as needed)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.ui.striped.celled.table"))
        )
        
        # 4. Locate the table rows
        table = driver.find_element(By.CSS_SELECTOR, "table.ui.striped.celled.table")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        
        # 5. Loop through each row and extract relevant columns
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 11:
                continue  # skip incomplete rows
            
            for cell in cells:
                print(cell.text, end=" | ")

            challenger = cells[0].text.strip()
            opponent   = cells[2].text.strip()
            bot        = cells[5].text.strip()
            
            # 6. Grab the "Game Log" link (presumably in column 10)
            #    and build an absolute URL if needed
            try:
                game_log_anchor = cells[10].find_element(By.TAG_NAME, "a")
                game_log_url = game_log_anchor.get_attribute("href")
                
                # Build a (challenger, opponent, bot) key
                key = (challenger, opponent, bot)
                counters[key] = counters.get(key, 0) + 1

                # Create a filename for the game log
                filename = f"{challenger}_{opponent}_{bot}_{counters[key]}.txt"
                filename = filename.replace("/", "_").replace("\\", "_")  # Safety for file paths

                # 7. Open the log link in the same driver to ensure authentication is kept
                driver.execute_script(f"window.open('{game_log_url}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])  # switch to new tab

                # Wait a moment for the log to load (adjust as needed)
                time.sleep(2)

                # 8. Grab the log text. Sometimes the log is served directly as text/plain,
                #    or it might be in a <pre> block; adapt to your actual page structure.
                raw_text = driver.find_element(By.TAG_NAME, "body").text

                # 9. Write it to a file
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(raw_text)

                print(f"Saved {filename}")
            except:
                print("Failed to get game log for this row.")

            # Close the current log tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

    # Done. Close the browser if you like:
    driver.quit()

if __name__ == "__main__":
    scrape_with_selenium()