import selenium
from selenium import webdriver
import time

driver = selenium.webdriver.Chrome()
raw_url = "https://amzscout.net/sales-estimator/"
driver.get(raw_url)
driver.find_element_by_class_name('s-cat-icon-kitchen').click()
button_xpath = '//input[@class="form-control cat-rank_input js-disable"]'
driver.find_element_by_xpath(button_xpath).click()
time.sleep(0.5)
driver.find_element_by_xpath(button_xpath).send_keys('18000')
time.sleep(0.5)
calculate_button_xpath = '//button[@class="cat-rank_submit btn js-disable"]'
driver.find_element_by_xpath(calculate_button_xpath).click()
time.sleep(2)
# try_click = 3
# while try_click:
sales = print(driver.find_element_by_class_name('cat-rank_sales-val').text)
print(sales)
    # if not sales or sales is "?":
    #     try_click -= 1
driver.close()