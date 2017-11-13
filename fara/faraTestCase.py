import unittest
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os, shutil

class TestFaraSpider(unittest.TestCase):

    fara_gov_url = "https://google.com.ng"        

    def setUp(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.driver = webdriver.Firefox()

    # This script removes files in the snapshots folder so as to save new ones
        folder = 'snapshots'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def test_spider_supposed_actions(self):
        # Create an Instances of Driver
        driver = self.driver
        follow_links_driver = self.driver

        # Enter into the fara.gov search page
        driver.get(self.fara_gov_url)
        driver.save_screenshot('snapshots/screen_fara_gov_url.png')

        # Find and Proceed into Search Page by URL
        search_page_url = driver.find_elements(By.XPATH, "//iframe")[0].get_attribute("src")
        driver.get(search_page_url)
        driver.save_screenshot('snapshots/screen_search_page_url.png')

        # Find and Proceed into Active Principal Page by URL
        active_principal_url = driver.find_elements(By.XPATH, '//*[@id="L80330217189774968"]/li[1]/a')[0].get_attribute("href")
        driver.get(active_principal_url)
        driver.save_screenshot('snapshots/screen_active_principal_url.png')

        # Verify that We have Certain HTML tags in place
        # Since we do not know the actual Element, So we just check if the key elements exist
        content_table = driver.find_elements(By.XPATH, '//table[@class="apexir_WORKSHEET_DATA"]')
        try:
            self.assertGreaterEqual(len(content_table), 1)
        except AssertionError, err:
            message = err.args[0]
            message += "\nCannot Find Table that contains Active Principals"
            err.args = (message,) #wrap it up in new tuple
            raise
            
        country_name_header = driver.find_elements(By.XPATH, '//th[@class="apexir_REPEAT_HEADING"]/span[@class="apex_break_headers"]')
        try:
            self.assertGreaterEqual(len(country_name_header), 1)
        except AssertionError, err:
            message = err.args[0]
            message += "\nCannot Country Name Headers"
            err.args = (message,) #wrap it up in new tuple
            raise
        
        even_tr = driver.find_elements(By.XPATH, '//tr[@class="even"]')
        try:
            self.assertGreaterEqual(len(even_tr), 1)
        except AssertionError, err:
            message = err.args[0]
            message += "\nCannot TR Elements with Even class"
            err.args = (message,) #wrap it up in new tuple
            raise

        odd_tr = driver.find_elements(By.XPATH, '//tr[@class="odd"]')
        try:
            self.assertGreaterEqual(len(odd_tr), 1)
        except AssertionError, err:
            message = err.args[0]
            message += "\nCannot TR Elements with Odd Class"
            err.args = (message,) #wrap it up in new tuple
            raise

        # Validate that the main data points are available
        data_points = ['REG_DATE','FP_NAME','STATE','REG_NUMBER','REGISTRANT_NAME']
        for point in data_points:
            SELECTOR = '//td[contains(@headers, "'+ point +'")]'
            points_available = driver.find_elements(By.XPATH, SELECTOR)
            try:
                self.assertGreaterEqual(len(points_available), 1)
            except AssertionError, err:
                message = err.args[0]
                message += "\nCannot find Data Point " + point
                err.args = (message,) #wrap it up in new tuple
                raise
        
        # Find Exhibit URL
        follow_links = driver.find_elements(By.XPATH, '//td[contains(@headers, "LINK")]/a')
        try:
            self.assertGreaterEqual(len(follow_links), 1)
            #Test if Exhibit URL Link exist of follow link page
            follow_links_driver.get(follow_links[0].get_attribute('href'))
            follow_links_driver.save_screenshot('snapshots/screen_follow_links_driver.png')

            follow_link_driver_exhibit_url = follow_links_driver.find_elements(By.XPATH, '//td[contains(@headers, "DOCLINK")]/a')
            try:
                self.assertGreaterEqual(len(follow_link_driver_exhibit_url), 1)
            except AssertionError, err:
                message = err.args[0]
                message += "\nExhibition File URL Links not found"
                err.args = (message,) #wrap it up in new tuple
                raise
        except AssertionError, err:
            message = err.args[0]
            message += "\nNo Link to Exhibit URL Page found"
            err.args = (message,) #wrap it up in new tuple
            raise

    def tearDown(self):
        self.driver.close()
        self.display.stop()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFaraSpider)
    unittest.TextTestRunner(verbosity=2).run(suite)