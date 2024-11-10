import csv

# 定义输入的CSV文件路径和输出的TXT文件路径
input_csv = 'D:/Pycharm/Data/stockData/stockListName.csv'
output_txt = 'D:/data/data-for-1.7.5/data/dictionary/custom/上市公司.txt'

# 打开CSV文件
with open(input_csv, mode='r', encoding='utf-8') as file:
    # 使用csv.DictReader读取文件，这会将每行转换为字典，其中键是第一行中的字段名
    reader = csv.DictReader(file)

    # 打开或创建一个TXT文件用于写入
    with open(output_txt, mode='w', encoding='utf-8') as txt_file:
        # 遍历CSV文件中的每一行
        for row in reader:
            # 获取'name'列的值，并写入到TXT文件中
            name = row['name'].replace(' ', '')
            txt_file.write(name + ' '+'上市公司' + ' ' + '3' + '\n')

print("Name data has been successfully written to the text file.")