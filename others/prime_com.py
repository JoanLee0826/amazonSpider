import numpy as np
import pandas as pd
import requests, lxml
from lxml import etree
import re, time, random, datetime, time
import json

class AmazonGoods:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763"
    }
    proxies = {
        "http": "http://114.239.3.156:9999",
    }

    url_base = "https://www.amazon.com"
    s = requests.Session()
    s.get(url=url_base, headers=headers, proxies=proxies, verify=False)

    def __init__(self):
        self.goods_list = []

    def get_id(self, url):

        res = self.s.get(url, headers=self.headers, proxies=self.proxies, verify=False)

        if res.status_code != 200:
            print("请求出错，状态码为：%s" % res.status_code)
            print(res.text)
            return
        patt = re.compile(r'"sortedDealIDs" : [[](.*?)[]]', re.S)
        # return re.search(string=text, pattern=patt).group(1)
        row_list = re.search(string=res.text, pattern=patt).group(1).split(",")
        id_list = [{"dealID": each.strip().replace("\r\n", "").replace("\n", "")[1:-1]} for each in row_list]
        return id_list

    def get_req_json(self, id_list, start, end):
        try:
            sessionID = self.s.cookies.get('session-id')
            print(sessionID)
        except:
            sessionID = '147-0093206-6105777'
        req_json = {
            "requestMetadata": {"marketplaceID": "ATVPDKIKX0DER", "clientID": "goldbox_mobile_pc",
                                "sessionID": sessionID},
            "responseSize": "STATUS_ONLY", "itemResponseSize": "DEFAULT_WITH_PREEMPTIVE_LEAKING",
        }
        req_json['dealTargets'] = id_list[start:end]
        return req_json

    def get_data(self, req_json, i):
        # time_str = str(time.time()).replace(".", '')[:13]
        time_str = '1563177600123'
        req_url = "https://www.amazon.com/xa/dealcontent/v2/GetDealStatus" + "?nocache=" + time_str
        headers = {
            "Server": "Server",
            "Content-Type": "application/json",
            # "Content-Length": "704",
            "Strict-Transport-Security": "max-age=47474747; includeSubDomains; preload",
            # "x-amzn-RequestId": "f0419251-a767-11e9-a5f6-7b6a12dcce7e",
            # "X-Amz-Date": "Tue, 16 Jul 2019 01:20:46 GMT",
            "Vary": "Accept-Encoding,X-Amzn-CDN-Cache,X-Amzn-AX-Treatment,User-Agent",
            # "x-amz-rid": "99Z46S27MN34QKRDX9X1",
            "X-Frame-Options": "SAMEORIGIN",
            "Date": "Tue, 16 Jul 2019 01:20:46 GMT",
            "Connection": "keep-alive",
        }
        res = self.s.post(req_url, headers=headers, data=json.dumps(req_json))
        file_str = time.strftime('%m_%d_%H_%M', time.localtime()) + "_" + str(i)
        file_path = r'E:\\产品开发\\prime day 数据/'
        with open(file_path + "com_" + file_str + ".json", 'w') as f:
            f.write((json.dumps(res.json())))

    def run(self, url):
        id_list = self.get_id(url)
        for i in range(len(id_list)//100 + 1):
            req_json = self.get_req_json(id_list, i*100, i*100+100)
            self.get_data(req_json, i)

if __name__ == '__main__':
    prime = AmazonGoods()
    # url = "https://www.amazon.com/l/13887280011"
    # url = "https://www.amazon.com/b/ref=gbps_ftr_m-6_3b69_sort_BSEL?node=14611812011&gb_f_GB-SUPPLE=enforcedCategories:284507%252C1055398,dealTypes:DEAL_OF_THE_DAY%252CLIGHTNING_DEAL%252CBEST_DEAL,sortOrder:BY_BEST_SELLING,dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,MARKETING_ID:PDAY&gb_ttl_GB-SUPPLE=Deals%2520on%2520Home%2520and%2520Kitchen&pf_rd_p=db08f08d-45f1-490b-aa6c-1f4d543b3b69&pf_rd_s=merchandised-search-6&pf_rd_t=101&pf_rd_i=14611812011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=XDTVBNJEXKJ7Q0C8Q0KN&ie=UTF8"
    # hk 类目按照销量排序
    url = "https://www.amazon.com/b/ref=gbps_ftr_m-6_3b69_sort_BSEL?node=14611812011&gb_f_GB-SUPPLE=enforcedCategories:284507%252C1055398,dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,dealTypes:DEAL_OF_THE_DAY%252CLIGHTNING_DEAL%252CBEST_DEAL,sortOrder:BY_BEST_SELLING,MARKETING_ID:PDAY&gb_ttl_GB-SUPPLE=Deals%2520on%2520Home%2520and%2520Kitchen&pf_rd_p=db08f08d-45f1-490b-aa6c-1f4d543b3b69&pf_rd_s=merchandised-search-6&pf_rd_t=101&pf_rd_i=14611812011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=WEBYWNX4ZXZYRYCYGMKY&ie=UTF8"
    prime.run(url)


