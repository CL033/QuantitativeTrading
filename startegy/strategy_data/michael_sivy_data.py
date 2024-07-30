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
        # �������
        print(f"\nLength of strategy_data_list: {len(datalist)}\n")
        print("\n------------Begin add Datas------------\n")
        for i, fname in enumerate(tqdm(datalist)):
            # ��ȡCSV�ļ�
            df = pd.read_csv(
                fname,
                skiprows=0,
                header=0,
                encoding='GBK'
            )

            # ȷ����������Ϊ'datetime'��������ǣ����滻Ϊʵ�ʵ���������
            if 'date' not in df.columns:
                raise ValueError(f"CSV file {fname} does not contain a column named 'datetime'.")

            # ��datet��ת��Ϊdatetime����
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df.fillna(0, inplace=True)
            df = df.dropna()
            # ɸѡ������ʱ�䷶Χ������
            df = df[(df['date'] >= self.base_args.fromdate) & (df['date'] <= self.base_args.todate)]

            if len(df) == 0:
                print('bad ############', fname)
                continue
            # ������ʱ�ļ������ڴ洢ɸѡ������
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
            ticker = fname[-13:-4]  # ���ļ�����Ϊ����
            cerebro.adddata(data, name=ticker)
        print("\n------------Finish add Datas------------!\n")
