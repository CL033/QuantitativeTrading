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


def michael_sivy_filter(stockDatas):
    average_equity_ratio = stockDatas['equity_ratio'].mean()
    average_current_ratio = stockDatas['current_ratio'].mean()

    # 筛选符合条件的行：equity_ratio大于平均equity_ratio且current_ratio小于平均current_ratio
    selected_rows = stockDatas[(stockDatas['equity_ratio'] > average_equity_ratio) & (stockDatas['current_ratio'] < average_current_ratio)]

    # 提取对应的code
    selected_codes = selected_rows['code'].tolist()
    # equityRatio_values = [d.equity_ratio for d in stockDatas if len(d) > 0 and d.datetime.date(0) == currentDate]
    # avg_equityRatio = np.nanmean(equityRatio_values) if equityRatio_values else 0
    #
    # currentRatio_values = [d.current_ratio for d in stockDatas if len(d) > 0 and d.datetime.date(0) == currentDate]
    # avg_currentRatio = np.nanmean(currentRatio_values) if currentRatio_values else 0
    #
    # peTTm_values = [d.pe_ttm for d in stockDatas if len(d) > 0 and d.datetime.date(0) == currentDate]
    # avg_peTTm = np.nanmean(peTTm_values) if peTTm_values else 0
    #
    # EPS_values = [d.EPS for d in stockDatas if len(d) > 0 and d.datetime.date(0) == currentDate]
    # avg_EPS = np.nanmean(EPS_values) if EPS_values else 0
    #
    # dvRatio_values = [d.dv_ratio for d in stockDatas if len(d) > 0 and d.datetime.date(0) == currentDate]
    # avg_dvRatio = np.nanmean(dvRatio_values) if dvRatio_values else 0
    #
    # selected_stocks = [
    #     d for d in stockDatas
    #     if len(d) > 0  # 至少要有一根实际bar
    #        and d.datetime.date(0) == currentDate
    #        and not np.isnan(d.equity_ratio)  # 确保不是NaN
    #        and not np.isnan(d.dv_ratio)
    #        and not np.isnan(d.pe_ttm)
    #        and not np.isnan(d.EPS)
    #        and not np.isnan(d.dv_ratio)
    #        and d.dv_ratio > avg_dvRatio  # 股息率大于平均值
    #        and d.EPS > avg_EPS  # 每股收益增长率大于市场平均值
    #        and d.equity_ratio < avg_equityRatio  # 产权比率小于市场平均值
    #        and d.current_ratio > avg_currentRatio  # 流动比率大于市场平均值
    #        and 0 < d.pe_ttm < avg_peTTm  # 市盈率为正且小于市场平均值
    # ]
    return selected_codes
