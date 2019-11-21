import pandas as pd
import requests
from lxml import etree
import re, time


class BSR:
    info_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }

    proxies = {
        "http": "http://49.86.181.43:9999",
    }

    url_base = "https://www.amazon.com"
    s = requests.Session()
    s.headers.update(headers)
    s.get(url=url_base, headers=headers, proxies=proxies, verify=False)

    def parse(self, url):

        res = self.s.get(url=url, headers=self.headers, proxies=self.proxies, verify=False)
        res_html = etree.HTML(res.text)
        try:
            category = res_html.xpath("//span[@class='category']/text()")[0]
        except:
            category = None
        goods_content = res_html.xpath("//li[@class='zg-item-immersion']")
        for each in goods_content:
            try:
                rank_in = each.xpath(".//span[@class='zg-badge-text']/text()")[0]
            except:
                rank_in = None
            try:
                goods_url = each.xpath(".//a[@class='a-link-normal']/@href")[0]
                goods_url = 'https://www.amazon.com' + goods_url.split("ref")[0]
            except:
                goods_url = None

            try:
                ASIN = re.search('dp/(.*)/', goods_url).group().split("/")[1]

            except:
                ASIN = None
                print("商品排名{}处: ASIN解析出错/该商品已下线".format(rank_in))
            try:
                goods_review_str = each.xpath(".//a[@class='a-size-small a-link-normal']/text()")[0]
                goods_review_count = int(goods_review_str.replace(',', ''))
            except:
                goods_review_count = 0
            self.info_list.append((category, rank_in, ASIN, goods_url, goods_review_count))
            #     # pic_url = each.xpath(".//div[@class='a-section a-spacing-small']/img/@src")[0]
            #
            #     # res_pic = s.get(pic_url, headers=headers, proxies=proxies, verify=False)
            #     # file_name = r'E:\爬虫pycharm\data\pic\\' + ASIN + '.png'
            #     with open(file_name, "wb") as f:
            #         f.write(res_pic.content)
            #         time.sleep(random.random())
            # except Exception as e:
            #     print(e)
    def run(self, url):
        url_2 = url + '?&pg=2'
        self.parse(url=url)
        time.sleep(2)
        self.parse(url=url_2)

        aft = "_" + time.strftime("%m_%d_%H_%M", time.localtime())
        col = ['category', 'rank_in', 'ASIN', 'goods_url', 'goods_review_count']
        data_pd = pd.DataFrame(self.info_list, columns=col)
        file_path = r'E:\爬虫pycharm\data\category\\'
        category = data_pd['category'][0]
        print('{}类目下的{}条数据收集完毕'.format(category, len(data_pd)))
        data_pd.to_excel(file_path + category + aft + '.xlsx', encoding='utf-8',engine='xlsxwriter')

if __name__ == '__main__':

    bsr = BSR()
    url = 'https://www.amazon.com/gp/bestsellers/baby-products/302876011/'
    bsr.run(url)