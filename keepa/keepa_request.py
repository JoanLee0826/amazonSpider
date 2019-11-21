import requests
import pandas as pd
from dateutil.parser import parse
import urllib
import json
from jsonpath import jsonpath
from selenium import webdriver
import time, random, re, datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

KEEPA_KEY = '7sommorss711l4ci5f3n97ftgvcq8jm7tak3316h3a61jkifqq3qh3keebkm9rsl'  # keepa密钥
domain = '1'  # 亚马逊的市场 美国为1
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}  # 关闭图片，响应更快
chrome_opt.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(executable_path=r'E:\爬虫pycharm\others\chromedriver.exe', chrome_options=chrome_opt)
chrome_opt.add_argument('--headless')

def get_keepa_time(date):
    """
    把普通的时间格式转化为keep时间格式
    :param date:
    :return:
    """
    return int(time.mktime(parse(date).timetuple())/60-21564000)


cate_info = {
    "Apps & Games": 2350149011,
    "Baby Products": 165796011,
    "Digital Music": 163856011,
    "Toys & Games": 165793011,
    "Patio, Lawn & Garden": 2972638011,
    "Books": 283155,
    "Arts, Crafts & Sewing": 2617941011,
    "Software": 229534,
    "Sports & Outdoors": 3375251,
    "Handmade Products": 11260432011,
    "Video Games": 468642,
    "Clothing, Shoes & Jewelry": 7141123011,
    "Office Products": 1064954,
    "Grocery & Gourmet Food": 16310101,
    "Tools & Home Improvement": 228013,
    "Movies & TV": 2625373011,
    "Musical Instruments": 11091801,
    "Appliances": 2619525011,
    "Collectibles & Fine Art": 4991425011,
    "Pet Supplies": 2619533011,
    "Industrial & Scientific": 16310091,
    "Cell Phones & Accessories": 2335752011,
    "Everything Else": 10272111,
    "Home & Kitchen": 1055398,
    "Beauty & Personal Care": 3760911,
    "CDs & Vinyl": 5174,
    "Electronics": 172282,
    "Automotive": 15684181,
    "Health & Household": 3760901,
    "Vehicles": 10677469011,
}


def get_selection(
        category=1055398,
        rank_in=3000,
        rank_out=30000,
        review_count=60,
        date_in='2019-1-1',
        date_out='2019-9-15',
    ):
    queryJson = {
         "current_SALES_gte": rank_in,  # 最高排名
         "current_SALES_lte":  rank_out,  # 最底排名
         "current_COUNT_REVIEWS_gte": 0,  # 最低评价数量
         "current_COUNT_REVIEWS_lte": review_count,  # 最高评价数量
         "current_NEW_FBA_gte": 2000,  # FBA发货价格 最低20刀
         "current_NEW_FBA_lte": 5000,
         "avg30_NEW_FBA_gte": 2000,  # 30天平均最低发货价格20刀
         "avg30_NEW_FBA_lte": 5000,
         "trackingSince_gte": get_keepa_time(date_in),  # 跟踪时间不早于
         "trackingSince_lte": get_keepa_time(date_out),  # 跟踪时间不晚于
         "rootCategory": category,  # 跟类目节点
         "packageLength_gte": 1,
         "packageLength_lte": 450,
         "packageWidth_gte": 1,
         "packageWidth_lte": 450,
         "packageHeight_gte": 1,
         "packageHeight_lte": 450,  # 打包最大边长不高于450mm
         "packageWeight_gte": 1,
         "packageWeight_lte": 1800,  # 打包重量不高于1800g
         "sort": [["current_SALES", "asc"]],
         "lastOffersUpdate_gte": 4631500,  # int(time.time()/60-21564000)
         "lastRatingUpdate_gte": 4615660,
         "productType": [0, 1, 5],   # 0 所有产品， 1
         "perPage": 3000,  # 每一页展示的数据
         "page": 0  # 第几页
    }
    return queryJson


def get_asin():
    cate_key = 'Home & Kitchen'
    rank_in = 3000
    rank_out = 30000

    url = "https://api.keepa.com/query?key=" + KEEPA_KEY + "&domain=" + domain + '&selection=' + \
          urllib.parse.quote(json.dumps(get_selection(category=cate_info[cate_key],
                                                      rank_in=rank_in,
                                                      rank_out=rank_out)))
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/77.0.3865.120 Safari/537.36'
    })
    print(url)
    rep_data = s.get(url, verify=False)
    print(rep_data.text)
    file_name = "asin_list_" + datetime.datetime.now().strftime('%m%d%H%M') + '_' + cate_key + '_' + \
                str(rank_in) + '_' + str(rank_out) + '.csv'
    data_pd = pd.DataFrame(rep_data.json()['asinList'], columns=['ASIN'])
    data_pd.to_csv(file_name, encoding='utf-8')

    return data_pd


def get_varies(asin):
    asin_info = get_asin_info(asin)
    try:
        variations = jsonpath(asin_info, '$..products[0].variations')[0]
        parent_asin = jsonpath(asin_info, '$..products[0].parentAsin')[0]
    except:
        print("keepa 未返回ASIN数据信息")
        return None
    info_list = []
    if not parent_asin:
        parent_asin = asin
    if not variations:
        parent_info = get_asin_info(parent_asin)
        variations = jsonpath(parent_info, '$..products[0].variations')[0]
    for each_asin in variations:
        asin = each_asin.get('asin', None)
        try:
            stock, model = get_stock(asin)
        except:
            print('{}请求失败'.format(asin))
            stock, model = None, None
        para_list = []
        para = ''
        for each_para in each_asin.get('attributes'):
            para_list.append(each_para.get('value'))
            para = "-".join(para_list)
        info_list.append((parent_asin, asin,  para, stock, model))
    print(info_list)
    return info_list


def get_asin_info(ASIN):
    s = requests.Session()
    url = "https://api.keepa.com/product?key=" + KEEPA_KEY + "&domain=" + domain + "&update=-1" + "&asin=" + ASIN
    print(url)
    res_json = s.get(url).json()
    if res_json.get('products')[0]:
        return res_json
    else:
        return None


def get_stock(asin):
    def set_number(each, count=999):
        each.click()
        time.sleep(random.random())
        each.send_keys(Keys.BACKSPACE)
        each.send_keys(count)
        time.sleep(random.random())
        driver.find_element_by_xpath("//span[@class='a-button a-button-primary a-button-small sc-update-link']").click()

    asin_url = "https://www.amazon.com/dp/" + asin
    if not asin:
        print("没有ASIN输入")
        return None, None
    try:
        time.sleep(random.random())
        driver.get(asin_url)
        driver.set_page_load_timeout(15)
    except:
        print('打开链接失败')
    time.sleep(random.uniform(1.5, 2))

    try:
        is_stock = driver.find_element_by_id('availability').text
        if re.search('Available', is_stock):
            stock, model = None, 'another_seller'
            print('{}该链接卖家状态不可售，存在其他卖家'.format(asin_url))
            return stock, model
    except:
        pass

    try:
        # WebDriverWait(driver, 超时时长, 调用频率, 忽略异常).until(可执行方法, 超时时返回的信息)
        WebDriverWait(driver, 20, 0.5).until(ec.element_to_be_clickable((By.XPATH, "//input[@id='add-to-cart-button']")))
        driver.find_element_by_xpath("//input[@id='add-to-cart-button']").click()
        time.sleep(random.uniform(1, 2))
    except:
        print('加入购物车失败')
        # get_stock(asin)

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
        stock, model = None, None
        set_number(each, 999)
        time.sleep(random.uniform(2, 3))
        WebDriverWait(driver, 20, 0.5).until_not(
            ec.element_to_be_clickable((By.XPATH, "//span[@class='a-button a-button-primary a-button-small sc-update-link']")))
        try:
            stock_value = driver.find_element_by_xpath("//input[@name='quantityBox']").get_attribute('value')
            stock = stock_value
        except:
            pass
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
            # try:
            #     delete_click = driver.find_elements_by_xpath("//input[@value='Delete']")
            try:
                if driver.find_elements_by_xpath("//input[@value='Delete']"):
                    time.sleep(random.random())
                    driver.find_element_by_xpath("//input[@value='Delete']").click()
                    driver.refresh()
                    continue
                else:
                    break
            except:
                pass
        return stock, model


if __name__ == '__main__':
    get_varies('B07ZRD63C7')