from keepa_request import get_varies
import pandas as pd
import datetime
import pymysql

def stock_handle(file):
    stock_list = []
    # data = pd.read_excel(file)
    # asin_list = data['asin'].tolist()
    asin_list = ['B07PY3SKY2']
    for asin in asin_list:
        stock_list.extend(get_varies(asin))
        print(stock_list)

    aft = "stock_" + datetime.datetime.now().strftime("%m%d%H%M")
    data_pd = pd.DataFrame(stock_list, columns=['parent_asin', 'asin', 'style', 'stock', 'model'])
    data_pd.drop_duplicates(subset=['asin'], inplace=True)
    data_pd.to_excel(aft + '.xlsx')

    conn = pymysql.connect(host='localhost', port=3306, db='amazon_test', user='root', passwd='1118')
    cs = conn.cursor()
    for each in data_pd.values.tolist():
        parent_asin, asin, style, stock, model = each
        stock_date = datetime.datetime.now()
        insert_sql = "INSERT INTO amazon_test.amazon_stock(parent_asin, asin, style, stock, model, stock_date) VALUES" \
                     "(%s,%s,%s,%s,%s,%s)"

        count = cs.execute(insert_sql, (parent_asin, asin, style, stock, model, stock_date))
        print(count)
        try:
            conn.commit()
        except:
            conn.rollback()

    cs.close()



if __name__ == '__main__':
    file = r'E:\爬虫pycharm\data\goods_detail\目标产品.xlsx'
    stock_handle(file)