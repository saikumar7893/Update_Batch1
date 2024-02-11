import os
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

class JobScraperInsightGlobal:
    class OutputManager:
        def __init__(self, base_folder):
            self.base_folder = base_folder

        def create_folder(self, folder_name):
            folder_path = os.path.join(self.base_folder, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            return folder_path

        def create_subfolder_with_date(self):
            today_date = date.today().strftime("%Y-%m-%d")
            subfolder_path = self.create_folder(today_date)
            return subfolder_path

        def append_or_create_csv(self, subfolder_path, csv_name, data):
            csv_path = os.path.join(subfolder_path, csv_name)

            if os.path.exists(csv_path):
                existing_data = pd.read_csv(csv_path)
                updated_data = pd.concat([existing_data, data], ignore_index=True)
                updated_data.to_csv(csv_path, index=False)
                print(f"Appended data to existing CSV: {csv_path}")
            else:
                data.to_csv(csv_path, index=False)
                print(f"Created new CSV: {csv_path}")

    def __init__(self):
        self.output_manager = self.OutputManager('output')
        self.company_name = "Insight Global"
        self.keywords = ["Data Analyst", "Business Analyst", "System Analyst", "Data Scientists", "Data engineer", "Business System Analyst"]
        self.previous_jobs = self.load_previous_jobs()

    def load_previous_jobs(self):
        previous_jobs = {}
        # Load previous jobs from CSV or database if available
        return previous_jobs

    def save_new_jobs(self):
        # Save new jobs to CSV or database for comparison in future runs
        pass

    def scrape_jobs(self):
        for user_input in self.keywords:
            print(f"Scraping data for the job role: {user_input}...")
            new_jobs = {}  # Dictionary to store the newly fetched jobs
            i = 2

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)

            driver.get("https://jobs.insightglobal.com/")
            driver.maximize_window()

            search_bar = driver.find_element(By.XPATH, '//input[@placeholder="Title or keyword"]')
            search_bar.send_keys(user_input)
            search_icon = driver.find_element(By.XPATH, '//input[@id="homesearch"]')
            search_icon.click()

            while True:
                jobs = driver.find_elements(By.XPATH, '//div[@class="result"]')
                for job in jobs:
                    job_no = int(job.get_attribute("data-id"))
                    job_title = job.find_element(By.XPATH, './/div[@class="job-title"]//a')

                    if job_no not in self.previous_jobs:
                        self.previous_jobs[job_no] = True
                        job_Posted_Date = job.find_element(By.XPATH, './/p[@class="date"]').text
                        job_url = job_title.get_attribute('href')
                        details = job.find_elements(By.XPATH, './/div[@class="job-info"]//p')

                        list1 = [detail.text for detail in details]
                        job_location = list1[0]
                        job_Type = list1[2]
                        pay_rate = list1[3] if len(list1) > 3 else "NA"

                        if 'contract' in job_Type.lower():
                            list1 = [self.company_name, date.today().strftime("%d/%m/%Y"), job_title.text, job_Type, pay_rate,
                                     job_url, job_location, job_Posted_Date, "855-485-8853", "NA"]
                            list1 = ['NA' if value == '' else value for value in list1]
                            new_jobs[job_no] = list1

                next_url = f"https://jobs.insightglobal.com/jobs/find_a_job/{i}/?rd=Distance&remote=false&miles=False&srch={user_input.replace(' ', '+')}"
                driver.get(next_url)
                if i == 10:
                    break
                i += 1
                time.sleep(2)

            driver.quit()
            self.save_new_jobs()  # Save the new jobs for comparison in future runs
            if new_jobs:
                self.generate_csv(new_jobs)

    def generate_csv(self, new_jobs):
        subfolder = self.output_manager.create_subfolder_with_date()

        npo_jobs_df = pd.DataFrame.from_dict(new_jobs, orient='index',
                                             columns=['Vendor Company Name', 'Date & Time Stamp', 'Job Title',
                                                      'Job Type', 'Pay Rate', 'Job Posting Url', 'Job Location',
                                                      'Job Posting Date', 'Contact Person', 'Work Type (Remote /Hybrid /Onsite)'])

        file_name = 'job_portal.csv'
        self.output_manager.append_or_create_csv(subfolder, file_name, npo_jobs_df)
        print(f"CSV file '{file_name}' has been generated.")

# Example usage:
if __name__ == "__main__":
    insight_global_scraper = JobScraperInsightGlobal()
    insight_global_scraper.scrape_jobs()
