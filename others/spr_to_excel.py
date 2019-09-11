import json
import numpy as np
import pandas as pd
import os


def scan(file_path):
    for file in os.listdir(file_path):
        file_real = file_path + "/" + file
        if os.path.isdir(file_real):
            scan(file_real)
        else:
            if file_real.endswith("json"):
                file_handle(file_real)

def file_handle(file):
    file_path, file_name = os.path.split(file)
    data_path = file_path + "/excel数据/"
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    with open(file, 'rb') as f:
        data = f.readlines()[0]
    res_data = json.loads(data.decode('utf-8').strip('\ufeff')).get('data')
    pd_spr = pd.DataFrame(res_data)
    pd_spr['pic_table_url'] = '<table> <img src=' + '\"' +pd_spr['imageUrl'] + '\"' +'height="140" >'
    pd_spr.to_excel(data_path + file_name.replace('json','xlsx'), engine='xlsxwriter')
    print('json数据处理完毕')

if __name__ == '__main__':
    file_path = "E:\产品开发\产品开发\过程数据"
    # scan(file_path)
    file_handle(file_path + "/" + "spr_throw_pillows.json")