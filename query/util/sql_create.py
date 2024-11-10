import pymysql
import os
import util.constant as CONSTANT
from pathlib import Path
# 数据库配置信息
db_config = {
    'host': CONSTANT.DB_HOST,
    'user': CONSTANT.DB_USER,
    'password': CONSTANT.DB_PASSWORD,
    'database': CONSTANT.DB_DATABASE,
}

# 创建一个目录来存放生成的文件
current_dir = Path(os.path.abspath(__file__)).parent
output_dir = current_dir / 'train_data' / 'indu_table_creates'
os.makedirs(output_dir, exist_ok=True)

# 连接数据库
connection = pymysql.connect(**db_config)

try:
    with connection.cursor() as cursor:
        # 获取数据库中的所有表名
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        # 遍历每个表并获取其创建语句
        for table_name in tables:
            sql = f"SHOW CREATE TABLE {table_name}"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                create_table_sql = result[1]
                # 将创建语句写入到文件中
                file_path = os.path.join(output_dir, f"{table_name}.txt")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(create_table_sql)
                print(f"Table {table_name} create statement saved to {file_path}")
            else:
                print(f"Table {table_name} does not exist.")
finally:
    connection.close()