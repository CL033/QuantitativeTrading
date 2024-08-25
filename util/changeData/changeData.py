import pandas as pd
import os
from tqdm import tqdm


def change_report():
    folder_path = 'D:\\Pycharm\\Data\\stockData\\OShaughnessy\\yanjiusheng\\profit_and_cash_and_yeardate.csv'
    directory = os.path.dirname(os.path.abspath(folder_path))
    print(directory)
    # 创建'new'文件夹，如果它不存在
    new_folder_path = os.path.join(directory, 'new')
    os.makedirs(new_folder_path, exist_ok=True)
    try:
        df = pd.read_csv(folder_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(folder_path, encoding='ANSI')
        except UnicodeDecodeError:
            df = pd.read_csv(folder_path, encoding='gbk')
    # 按照 'stage' 字段进行分组
    # 按照 'stage' 字段进行分组
    grouped = df.groupby('stage')

    # 定义一个函数来转换stage为代表性的文件名
    def get_representative_filename(stage):
        if '一季报' in stage:
            return f"{stage[:4]}_q1.csv"
        elif '中报' in stage:
            return f"{stage[:4]}_q2.csv"
        elif '三季报' in stage:
            return f"{stage[:4]}_q3.csv"
        elif '年报' in stage:
            return f"{stage[:4]}_annual.csv"
        else:
            return f"{stage[:4]}_unknown.csv"

    # 遍历每个组并将其保存为单独的CSV文件
    for stage, group in grouped:
        # 使用自定义函数生成文件名
        filename = os.path.join(new_folder_path, get_representative_filename(stage))

        # 保存该组数据到CSV文件
        group.to_csv(filename, index=False, encoding='utf-8-sig')


def delete_column():
    folder_path = 'D:\\Pycharm\\Data\\stockData\\OShaughnessy\\yanjiusheng\\new'

    # 获取 'new' 文件夹下所有的 CSV 文件
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # 遍历每个 CSV 文件
    for file in csv_files:
        # 构建完整的文件路径
        file_path = os.path.join(folder_path, file)

        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        # 检查并删除指定的列
        columns_to_drop = ['stage', 'year', 'trade_date']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

        # 保存修改后的文件，覆盖原文件
        df.to_csv(file_path, index=False, encoding='utf-8-sig')

    print("所有文件处理完成，指定列已删除。")


def change_dailyData():
    # 设置输入文件路径
    input_file_path = 'D:\\Pycharm\\Data\\stockData\\OShaughnessy\\yanjiusheng\\backtest_data.csv'
    # 获取输入文件所在的目录
    directory = os.path.dirname(os.path.abspath(input_file_path))
    # 创建 'codes' 文件夹用于保存新文件
    codes_folder_path = os.path.join(directory, 'codes')
    os.makedirs(codes_folder_path, exist_ok=True)
    # 读取CSV文件
    try:
        df = pd.read_csv(input_file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(input_file_path, encoding='ANSI')
        except UnicodeDecodeError:
            df = pd.read_csv(input_file_path, encoding='gbk')
    # 按照 'code' 字段进行分组
    grouped = df.groupby('ts_code')
    # 遍历每个组并将其保存为单独的CSV文件
    for code, group in tqdm(grouped, desc="Processing codes", unit="file"):
        # 生成文件名，例如 "000001.SZ.csv"
        filename = os.path.join(codes_folder_path, f"{code}.csv")

        # 保存该组数据到CSV文件
        group.to_csv(filename, index=False, encoding='utf-8-sig')
    print("所有文件处理完成，并已保存到 'codes' 文件夹中。")


def change_column():
    global columns
    # 获取当前目录下的new文件夹路径
    # folder_path = 'D:\\Pycharm\\Data\\testData\\OShaughnessy'
    folder_path = 'D:\\Pycharm\\Data\\stockData\\OShaughnessy\\dailyData2'
    # 获取new文件夹下的所有CSV文件
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    # 要提取的列，并将trade_date放在第一列
    columns = ['trade_date', 'ts_code', 'open', 'high', 'low', 'close_x', 'vol', 'dv_ratio','total_share', 'total_mv']
    # 遍历每个CSV文件
    for csv_file in tqdm(csv_files):
        file_path = os.path.join(folder_path, csv_file)

        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 只保留所需的列，并将trade_date放在第一列
        df_filtered = df[columns]

        # 将处理后的数据保存回CSV文件
        df_filtered.to_csv(file_path, index=False, encoding='utf-8-sig')
    print("所有文件已处理完毕。")


# change_column()

# change_dailyData()

# # 获取所有的csv文件
# delete_column()

# # 获取输入文件所在的目录
# change_report()
