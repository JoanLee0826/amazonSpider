import numpy as np
import pandas as pd
import requests
from lxml import etree
import datetime, time, random
from queue import Queue
import threading
import pymysql



class BSE:
    headers = {

        'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0);'
    }

    # 添加代理 应添加https生效 实际操作中会用到全局VPN
    proxies = {
        "http": "http://49.86.181.43:9999",
    }

    # 写入数据库 待完善
    # db = pymysql.connect(host='localhost', port=3306, db='amazon_test',
    #                      user='root', passwd='1118', charset='utf8')

    s = requests.Session()
    s.headers.update(headers)
    url_base = "https://www.amazon.com"
    s.get(url=url_base, headers=headers, proxies=proxies, verify=False)

    raw_queue = Queue()
    fir_queue = Queue()
    sec_queue = Queue()
    thr_queue = Queue()
    thr_list = []
    last_list = []


    def del_ref(self, url):
        try:
            url = url.split('/ref')[0]
        except:
            pass
        return url

    def get_raw(self):

        raw_base_url = r'https://www.amazon.com/Best-Sellers/zgbs/'
        raw_res = self.s.get(url=raw_base_url, headers=self.headers, proxies=self.proxies)
        raw_html = etree.HTML(raw_res.text)

        for each in raw_html.xpath('//*[@id="zg_browseRoot"]/ul/li')[-5:-4]:
            title = each.xpath("./a/text()")[0]
            url = each.xpath("./a/@href")[0]
            url = self.del_ref(url)
            print(title, '一级类目')
            print(url)
            self.raw_queue.put((title, url))
            print('raw_list:',self.raw_queue.qsize())

    def get_fir(self, abs_title, abs_url):

        abs_res = self.s.get(url=abs_url, headers=self.headers, proxies=self.proxies)
        abs_html = etree.HTML(abs_res.text)

        for each in abs_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/li'):
            fir_url = each.xpath("./a/@href")[0]
            fir_url = self.del_ref(fir_url)
            fir_title = each.xpath("./a/text()")[0]
            print(fir_title, '二级类目')
            print(fir_url, "")
            self.fir_queue.put((abs_title, abs_url, fir_title, fir_url))
            print('二级类目数据',self.fir_queue.qsize())

    def get_sec(self, abs_title, abs_url, fir_title, fir_url):

        inner_res = self.s.get(url=fir_url, headers=self.headers, proxies=self.proxies)
        inner_html = etree.HTML(inner_res.text)

        if inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/li/a'):
            for each in inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/li/a'):
                sec_url = each.xpath("./@href")[0]
                sec_url = self.del_ref(sec_url)
                sec_title = each.xpath("./text()")[0]
                print("get_sec")
                print(sec_title, "三级类目")
                print(sec_url)
                self.sec_queue.put((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url))
        else:
            self.last_list.append((abs_title, abs_url, fir_title, fir_url))
            print(len(self.last_list), self.last_list[-1][-2:])


    def get_thr(self, abs_title, abs_url, fir_title, fir_url, sec_title, sec_url):

        time.sleep(random.random())
        inner_res = self.s.get(url=sec_url, headers=self.headers, proxies=self.proxies)
        inner_html = etree.HTML(inner_res.text)

        if inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul/li/a'):

            for each in inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul/li/a'):
                thr_url = each.xpath("./@href")[0]
                thr_url = self.del_ref(thr_url)
                thr_title = each.xpath("./text()")[0]
                print("get_thr")
                print(thr_title, "四级类目")
                print(thr_url)
                self.thr_queue.put((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url))
                self.thr_list.append((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url))
                print(len(self.last_list), self.last_list[-1][-2:])

        else:
            self.last_list.append((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url))
            print(len(self.last_list), self.last_list[-1][-2:])


    def get_last(self, abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url):
        inner_res = self.s.get(url=thr_url, headers=self.headers, proxies=self.proxies)
        inner_html = etree.HTML(inner_res.text)

        if inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul/ul/li/a'):

            for each in inner_html.xpath('//*[@id="zg_browseRoot"]/ul/ul/ul/ul//ul/li/a'):
                last_url = each.xpath("./@href")[0]
                last_url = self.del_ref(last_url)
                last_title = each.xpath("./text()")[0]
                print("get_last")
                print(last_title, "子类目")
                print(last_url)
                self.last_list.append((abs_title, abs_url, fir_title, fir_url, sec_title, sec_url, thr_title, thr_url,
                                       last_title, last_url))
                print(len(self.last_list), self.last_list[-1][-2:])

    def run(self):

        self.get_raw()
        print(self.raw_queue.qsize())

        while True:

            fir_list = [threading.Thread(target=self.get_fir, args=(self.raw_queue.get())) for i in range(3)
                        if not self.raw_queue.empty()]

            for each in fir_list:
                each.start()
            for each in fir_list:
                each.join()
            time.sleep(0.5)

            sec_list = [threading.Thread(target=self.get_sec, args=(self.fir_queue.get())) for i in range(8)
                        if not self.fir_queue.empty()]

            for each in sec_list:
                each.start()
            for each in sec_list:
                each.join()
            time.sleep(random.random())

            thr_list = [threading.Thread(target=self.get_thr, args=(self.sec_queue.get())) for i in range(20)
                        if not self.sec_queue.empty()]

            for each in thr_list:
                each.start()
            for each in thr_list:
                each.join()
            time.sleep(random.random())

            final_list = [threading.Thread(target=self.get_last, args=(self.thr_queue.get())) for i in range(20)
                        if not self.thr_queue.empty()]

            for each in final_list:
                each.start()
            for each in final_list:
                each.join()
            time.sleep(random.random())

            if self.fir_queue.empty() and self.sec_queue.empty() and self.raw_queue.empty() and self.thr_queue.empty():
                break

        try:
            last_data = pd.DataFrame(self.last_list, columns=['类目名称','类目链接','二级类目','二级类目链接','三级类目',
                                                          '三级类目链接','四级类目','四级类目链接','子类目','子类目链接'])
            last_data.sort_values(by=['类目名称','二级类目','三级类目','四级类目','子类目'], ascending=True, inplace=True)
        except:
            last_data = pd.DataFrame(self.last_list)
        return last_data



if __name__ == '__main__':


    bse = BSE()
    aft = datetime.datetime.now().strftime('%m%d%H%M')
    file_name = r'../data/category/amazon_category_' + aft + '.xlsx'
    bse.run().to_excel(file_name, encoding='utf-8', engine='xlsxwriter')
