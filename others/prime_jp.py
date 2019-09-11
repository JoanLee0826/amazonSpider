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

    url_base = "https://www.amazon.co.jp"
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
        row_list = ",".join(re.findall(string=res.text, pattern=patt)).split(',')
        id_list = [{"dealID": each.strip().replace("\r\n", "").replace("\n", "")[1:-1]} for each in row_list]
        return id_list

    def get_id_list(self, file_path):
        # file_path = r'E:\产品开发\prime day 数据\excel数据\jp_07_16_13_29_0.xlsx'
        data_id = pd.read_excel(file_path)
        row_list = list(data_id['dealID'].drop_duplicates())
        id_list = [{"dealID": each.strip().replace("\r\n", "").replace("\n", "")} for each in row_list]
        return id_list

    def get_req_json(self, id_list, start, end):
        try:
            sessionID = self.s.cookies.get('session-id')
            print(sessionID)
        except:
            sessionID = '358-1080552-8818701'
        req_json = {
            "requestMetadata": {"marketplaceID": "A1VC38T7YXB528", "clientID": "goldbox_mobile_pc",
                                "sessionID": sessionID},
            "responseSize": "STATUS_ONLY", "itemResponseSize": "DEFAULT_WITH_PREEMPTIVE_LEAKING",
        }
        req_json['dealTargets'] = id_list[start:end]
        return req_json

    def get_data(self, req_json, i):
        time_str = str(time.time()).replace(".", '')[:13]
        # time_str = '1563177600123'
        req_url = "https://www.amazon.jp/xa/dealcontent/v2/GetDealStatus" + "?nocache=" + time_str
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
        file_str = time.strftime('%m_%d_%H_%M_%S', time.localtime()) + "_" + str(i)
        file_path = r'E:\\产品开发\\prime day 数据/'
        with open( file_path + "jp_vv" + file_str + ".json", 'w') as f:
            f.write((json.dumps(res.json())))

    def run(self, url, file_path):
        if url:
            id_list = self.get_id(url)
        if file_path:
            id_list = self.get_id_list(file_path)

        for i in range(len(id_list)//100 +1 ):
            req_json = self.get_req_json(id_list, i*100, i*100+100)
            print(req_json)
            self.get_data(req_json, i)


if __name__ == '__main__':


    prime = AmazonGoods()
    # url = "https://www.amazon.co.jp/l/4429743051"
    # url = "https://www.amazon.co.jp/l/4429743051/ref=gbph_ftr_m-9_d4f8_page_2?gb_f_ALLDEALS=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,sortOrder:BY_SCORE,MARKETING_ID:PD19%252CPDSD%252CPDAY%252CPDPMP%252CAMZDEVICES,enforcedCategories:2378086051&pf_rd_p=be15ea91-e4de-4b88-8304-dc735f19d4f8&pf_rd_s=merchandised-search-9&pf_rd_t=101&pf_rd_i=4429743051&pf_rd_m=AN1VRQENFRJN5&pf_rd_r=HB7NRNH10QTJAMK5R86P&gb_f_olsamazondevices=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CUPCOMING,page:2,sortOrder:BY_SCORE,MARKETING_ID:AMZDEVICES,dealsPerPage:4&ie=UTF8"
    # 寝具url
    # url ="https://www.amazon.co.jp/l/4429743051/ref=gbps_ftr_m-8_8a89_wht_23780860?gb_f_ALLDEALS=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,sortOrder:BY_SCORE,MARKETING_ID:PD19%252CPDSD%252CPDAY%252CPDPMP%252CAMZDEVICES,enforcedCategories:2378086051&pf_rd_p=4ac480f4-5fbf-4022-9ab8-9a887afc8a89&pf_rd_s=merchandised-search-8&pf_rd_t=101&pf_rd_i=4429743051&pf_rd_m=AN1VRQENFRJN5&pf_rd_r=NQH7DMGNQ80WK3C8FJMJ&ie=UTF8"
    # 寝具 home kitchen 户外 baby
    # url = "https://www.amazon.co.jp/l/4429743051/ref=gbps_ftr_m-8_8a89_wht_21272120?gb_f_ALLDEALS=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,sortOrder:BY_SCORE,MARKETING_ID:PD19%252CPDSD%252CPDAY%252CPDPMP%252CAMZDEVICES,enforcedCategories:2378086051%252C3828871%252C344845011%252C14304371%252C2127212051&pf_rd_p=4ac480f4-5fbf-4022-9ab8-9a887afc8a89&pf_rd_s=merchandised-search-8&pf_rd_t=101&pf_rd_i=4429743051&pf_rd_m=AN1VRQENFRJN5&pf_rd_r=NQH7DMGNQ80WK3C8FJMJ&ie=UTF8"
    # prime.run(url)
    file_path = r'E:\产品开发\prime day 数据\excel数据\jp_07_16_18_49_2.xlsx'
    prime.run(url=None, file_path=file_path)



