import numpy as np
import pandas as pd

# 指标计算

# 根据日收益率序列计算收益率与回撤率
def get_return_rate_from_pnl(pnl:pd.Series):
    cumulative = ((pnl + 1).cumprod() - 1).apply(lambda x:x*100 ).round(2)

    # 计算回撤序列
    max_return = cumulative.cummax()
    drawdown = (max_return - cumulative) / max_return
    drawdown.fillna(0,inplace=True)
    drawdown = drawdown.apply(lambda x:x*100 ).round(2)
    
    return cumulative,drawdown

# 根据收盘价计算收益率
def get_return_rate_from_pd(df:pd.DataFrame):
    df['earn_rate'] =( df['close'].pct_change()).apply(lambda x:x*100 ).round(2)
    df['syl']=((1+df['earn_rate']).cumprod()-1).apply(lambda x:x*100 ).round(2)
    return list(df.earn_rate.values)