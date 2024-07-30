import numpy as np


# 三低策略筛选方法
def chooseStock(stockData):
    # target_stock = pd.DataFrame()
    if 'peTTM' not in stockData.columns or 'pbMRQ' not in stockData.columns or 'psTTM' not in stockData.columns:
        raise ValueError("Input DataFrame must have columes 'peTTm' and 'pbMRQ' and 'psTTM'")
    target_stock = stockData[
        (stockData['peTTM'].between(10, 20)) & (stockData['pbMRQ'].between(0, 2)) & (stockData['psTTM'].between(0, 1))]
    # 对筛选出的股票进行成交量排序
    target_stock = target_stock.sort_values(by='volume', ascending=False)
    target_stock = target_stock.reset_index(drop=True)
    # 把code放入股票池之中
    choosedStock = target_stock['code'].tolist()
    return choosedStock


# 三低策略筛选方法
def filter_stocks_by_PS_PE_PB(stockDatas, currentDate):
    selected_stocks = [
        d for d in stockDatas
        if len(d) > 0  # 至少要有一根实际bar
           and d.datetime.date(0) == currentDate
           and 0 < d.peTTM < 20
           # and d.pbMRQ >= 0
           and d.close < 10
        # and d.psTTM >= 0
        # and d.psTTM <= 1
    ]
    return selected_stocks
