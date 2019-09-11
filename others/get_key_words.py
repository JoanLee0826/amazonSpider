from selenium import webdriver
import time, random
import pandas as pd
import os


def get_key(asin_list, market='JP'):
    info_list = []
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    raw_url = "https://www.sellersprite.com/cn/w/user/login"
    driver.get(raw_url)
    driver.find_element_by_name('email').send_keys('18852951102')
    driver.find_element_by_name('password_otn').send_keys('lu19940118')
    time.sleep(random.random())
    driver.find_element_by_id('login_btn').click()
    time.sleep(random.uniform(1.2,2))
    if driver.find_element_by_class_name('modal-dialog'):
        try:
            driver.find_element_by_xpath("//button[@data-bb-handler='confirm']").click()
        except:
            pass

    key_url = 'https://www.sellersprite.com/v2/keyword-reverse'

    driver.get(key_url)
    time.sleep(random.random())

    if market == 'US':
        key_url += '/US/'
    elif market == 'JP' or market == '':
        key_url += '/JP/'
    else:
        print("站点选择有误，美国站请选择'US'，日本站请选择'JP'")

    for asin in asin_list:
        url = key_url + asin
        driver.get(url)
        try:
            for i in range(1,5):
                key_words = driver.find_element_by_xpath("//tbody/tr["+ str(i) +"]/td[1]/a").text
                key_value = driver.find_element_by_xpath("//tbody/tr["+ str(i) +"]/td[2]/a").text
                key_score = driver.find_elements_by_xpath("//tbody/tr["+ str(i) +"]/td[3]/span").__len__()
                info_list.append((asin, i , key_words, key_value, key_score))
                time.sleep(random.uniform(2, 4))
        except:
            info_list.append((asin, None, None, None, None))
    data_df = pd.DataFrame(info_list, columns=['asin','关键词级别', '关键词', '关键词月搜索量', '关键词权重'])
    aft = time.strftime('%m%d%H%M', time.localtime())

    if not os.path.exists('./data'):
        os.mkdir('./data')

    data_df.to_excel('./data/'+ aft +'.xlsx')
    print('即将关闭浏览器')
    time.sleep(3)
    driver.close()

if __name__ == '__main__':

    market = input("请将asin列表写入文件asin_list.xlsx后运行此文件\r\n选择市场，默认为日本“JP”, 切换美国请输入“US”: ").upper()
    print('页面自动运行中， 请勿关闭')
    time.sleep(2)
    asin_list = list(pd.DataFrame(pd.read_excel('asin_list.xlsx')).asin)
    get_key(asin_list=asin_list, market=market)

