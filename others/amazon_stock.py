from selenium import webdriver
import pandas as pd
import time, random, re
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

info_list = []
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}  # 关闭图片，响应更快
chrome_opt.add_experimental_option("prefs", prefs)
# chrome_opt.add_argument('--headless')
driver = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=chrome_opt)


def get_stock(asin_list, market='US'):

    for asins in asin_list[-6:-3]:
        each_list = asins.strip('"').strip("[").strip("]").split(',')
        if len(each_list) > 10:
            print('ASIN变体数量过多，暂不考虑')
            continue
        for ASIN in each_list:
            ASIN = ASIN.replace("'", '').strip()
            asin_url = "https://www.amazon.com/dp/" + ASIN
            try:
                time.sleep(random.random())
                driver.get(asin_url)
                driver.set_page_load_timeout(15)
            except:
                continue
            time.sleep(random.uniform(1.5, 2))
            if driver.find_element_by_xpath("//input[@id='add-to-cart-button']"):
                try:
                    driver.find_element_by_xpath("//input[@id='add-to-cart-button']").click()
                    time.sleep(random.uniform(1, 2))
                except:
                    print('加入购物车失败')
            else:
                pass
            cart_url = 'https://www.amazon.com/gp/cart/view.html/'
            driver.get(cart_url)
            try:
                driver.set_page_load_timeout(20)
            except:
                print('购物车打开失败')

            ele_name = driver.find_elements_by_name("quantity")
            for each in ele_name:
                select = Select(each)
                select.select_by_value('10')

            text = driver.find_elements_by_name("quantityBox")
            for each in text:
                set_number(each, 999)
                time.sleep(random.uniform(2, 3))
                # driver.refresh()
                stock_value = driver.find_element_by_xpath("//input[@name='quantityBox']").get_attribute('value')
                stock = stock_value
                model = None
                try:
                    model_check = driver.find_element_by_xpath("//div[@class='a-alert-content']/"
                                                               "span[@class='a-size-base']").text
                    if re.search('available', model_check):
                        model = 'available'
                    if re.search('limit', model_check):
                        model = 'limit'
                except:
                    pass
                time.sleep(random.uniform(1.5, 2))
                while True:
                    try:
                        driver.find_element_by_xpath("//input[@value='Delete']").click()
                        break
                    except:
                        driver.refresh()
                        continue
                info_list.append([ASIN, stock, model])
                print(info_list[-1])

    print(pd.DataFrame(info_list, columns=['ASIN', 'stock', 'model']))
    time.sleep(5)
    driver.close()
    return data


def set_number(each, count=999):
    each.click()
    time.sleep(random.random())
    each.send_keys(Keys.BACKSPACE)
    each.send_keys(count)
    time.sleep(random.random())
    driver.find_element_by_xpath("//span[@class='a-button a-button-primary a-button-small sc-update-link']").click()


if __name__ == '__main__':
    # file = r'E:\爬虫pycharm\others\asin_list.xlsx'
    # data = pd.DataFrame(pd.read_excel(file), columns=['ASIN', 'stock', 'model'])
    file = r'E:\爬虫pycharm\data\goods_detail\目标产品.xlsx'
    data = pd.DataFrame(pd.read_excel(file))
    asin_list = data['multi_asin'].tolist()
    get_stock(asin_list=asin_list)
