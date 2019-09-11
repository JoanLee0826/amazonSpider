import json
import numpy as np
import pandas as pd
import os, time
import jsonpath


def scan(file_path):
    for file in os.listdir(file_path):
        file_real = file_path + "/" + file
        if os.path.isdir(file_real):
            scan(file_real)
        else:
            if file_real.endswith("json"):
                file_handle(file_real)

def file_handle(file):
    detail_list = []
    file_path, file_name = os.path.split(file)
    data_path = file_path + "/excel数据/"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    with open(file, 'rb') as f:
        data = f.readlines()[0]
    res_data = json.loads(data.decode())
    col = ['dealID', 'asin','lastUpdated', 'itemState', 'msCacheTtl', 'msToCustomerStateExpiry', 'percentClaimed',
                                    'totalCouponCount', 'waitlistChance', 'waitlistPosition']

    dealID_list = jsonpath.jsonpath(res_data, '$..dealStatus')
    # print(dealID_list)
    for each in list(dealID_list[0]):
        dealID = each
        for each in jsonpath.jsonpath(res_data, '$..' + each + "..dealItemStatus"):
            for i in each:
                lastUpdated = str(each[i]['lastUpdated'])[:10]
                lastUpdated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(lastUpdated)))
                # lastUpdated = time.ctime(int(lastUpdated))
                itemState = each[i]['itemState']
                msCacheTtl = each[i]['msCacheTtl']
                msToCustomerStateExpiry = each[i]['msToCustomerStateExpiry']
                percentClaimed = each[i]['percentClaimed']
                totalCouponCount = each[i]['totalCouponCount']
                waitlistChance = each[i]['waitlistChance']
                waitlistPosition = each[i]['waitlistPosition']

                detail_list.append((dealID, i, lastUpdated, itemState, msCacheTtl, msToCustomerStateExpiry, percentClaimed,
                                    totalCouponCount, waitlistChance, waitlistPosition))

    pd_pri = pd.DataFrame(detail_list, columns=col)
    pd_pri.to_excel(data_path + file_name.replace('json', 'xlsx'), engine='xlsxwriter')
    #

if __name__ == '__main__':

    file_path = r'E:\\产品开发\\prime day 数据'
    scan(file_path)
    # file_handle(file_path + "/" + "jp_07_17_09_55_0.json")