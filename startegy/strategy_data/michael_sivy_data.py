import backtrader as bt
from tqdm import tqdm
import pandas as pd
import tempfile
import util.constant as CONSTANT
import glob
import os
import datetime
from startegy.strategy_data.abstract_data import AbstractData


class PandasDataExtend(bt.feeds.GenericCSVData):
    pass


class MichaelSivyData(AbstractData):
    def read_data(self,cerebro):
        datadir = CONSTANT.DEFAULT_DIR + '/MicSivy/MicSivyData'
        datalist = glob.glob(os.path.join(datadir, '*.csv'))
        # 添加数据
        print(f"\nLength of strategy_data_list: {len(datalist)}\n")
        print("\n------------Begin add Datas------------\n")
        for i, fname in enumerate(tqdm(datalist)):
            # 读取CSV文件
            df = pd.read_csv(
                fname,
                skiprows=0,
                header=0,
                encoding='GBK'
            )

            # 确保日期列名为'datetime'，如果不是，请替换为实际的日期列名
            if 'date' not in df.columns:
                raise ValueError(f"CSV file {fname} does not contain a column named 'datetime'.")

            # 将datet列转换为datetime类型
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df.fillna(0, inplace=True)
            df = df.dropna()
            # 筛选出符合时间范围的数据
            df = df[(df['date'] >= self.base_args.fromdate) & (df['date'] <= self.base_args.todate)]

            if len(df) == 0:
                print('bad ############', fname)
                continue
            # 创建临时文件，用于存储筛选后数据
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                df.to_csv(temp_file.name, index=False, encoding='GBK')

            data = PandasDataExtend(
                dataname=temp_file.name,
                fromdate=self.base_args.fromdate,
                todate=self.base_args.todate + datetime.timedelta(days=1),
                nullvalue=0.0,
                dtformat=('%Y-%m-%d'),
                datetime=0,
                open=2,
                high=3,
                low=4,
                close=5,
                volume=7,
                openinterest=-1,
                plot=False
            )
            ticker = fname[-13:-4]  # 将文件名作为名字
            cerebro.adddata(data, name=ticker)
        print("\n------------Finish add Datas------------!\n")
