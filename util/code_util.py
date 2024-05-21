import akshare as ak
import pandas as pd
import  requests
from bs4 import BeautifulSoup
import json
index={'上证指数': 'sh000001',
        '深证成指': 'sz399001',
        '沪深300': 'sh000300',
        '创业板指': 'sz399006',
        '上证50': 'sh000016',
        '中证500': 'sh000905',
        '中小板指': 'sz399005',
        '上证180': 'sh000010'}

# 获取所有股票的代码
# def get_all_code():
#     url = 'http://47.103.76.149:8092/market/bsComInfo/allList'
#     page = requests.get(url)
#     data = pd.DataFrame(eval(BeautifulSoup(page.content, 'html.parser').text))
#     print(type(data.comCode))
#     return data.comCode
    # print(data)


# # 获取当前交易的股票代码和名称
# def get_code():
#     df = ak.stock_zh_index_spot()
#     codes = df['代码'].values
#     names = df['名称'].values
#     stock = dict(zip(names, codes))
#     # 合并指数和个股成一个字典
#     stocks = dict(stock, **index)
#     return stocks


# 获取行情数据
# def get_daily_data(code, start='20100101', end='20200716', adjust='hfq'):
#     # 如果代码在字典index里，则取的是指数数据
#     # code=get_code()[stock]
#     if code in index.values():
#         df = ak.stock_zh_index_daily_em(symbol=code, start_date=start, end_date=end)
#         # df = df[df.date.between(start,end)]
#     # 否则取的是个股数据
#     else:
#         df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust=adjust, start_date=start, end_date=end)
#         df.rename(columns={"日期": "date", "开盘": "open", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"},
#                   inplace=True)
#     if df.size == 0:
#         return pd.DataFrame(columns=['close', 'open', 'high', 'low', 'volume'])
#     # 将交易日期设置为索引值
#     df.index = pd.to_datetime(df.date)
#     df = df.sort_index()
#     # #计算收益率
#     # df['ret']=df.close/df.close.shift(1)-1
#     return df[['close', 'open', 'high', 'low', 'volume']]