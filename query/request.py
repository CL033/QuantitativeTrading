from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
import time
from selenium.webdriver.common.keys import Keys
from pathlib import Path
import os

# 设置WebDriver路径
driver_path = 'D:/Tools/WebDriver/edgedriver_win64/msedgedriver.exe'

current_dir = f'{str(Path(os.path.abspath(__file__)).parent)}/data'


def WenCai_WebSite(item_set):
    # 打开目标网站
    # driver.get('https://www.iwencai.com/stockpick/index')
    driver.get('https://www.iwencai.com/')
    time.sleep(3)
    for item in item_set:
        driver.find_element(By.CLASS_NAME, 'input-base-text')  # 这里的name或id取决于实际网站的搜索框属性
        driver.find_element(By.CLASS_NAME, 'input-base-text').send_keys(Keys.CONTROL, 'a')
        driver.find_element(By.CLASS_NAME, 'input-base-text').send_keys(item)
        time.sleep(1)
        try:
            suggestions = driver.find_element(By.CLASS_NAME, 'lenove-board')  # CSS选择器根据实际网站调整
            suggestions_list = suggestions.find_elements(By.TAG_NAME, 'li')
            # print(suggestions_list)
            # 打开一个文件用于写入，如果文件不存在则创建它
            with open(current_dir + '/output.txt', 'a', encoding='utf-8') as file:
                for suggestion in suggestions_list:
                    print(suggestion.text)
                    # 写入每一项suggestion.text到文件中，每项内容后面跟一个换行符
                    file.write(suggestion.text + '\n')
        except Exception as e:
            print(f"Error:{e}")
    # 关闭浏览器和服务
    driver.quit()
    service.stop()


def DongFang_WebSite(item_set):
    # 打开目标网站
    driver.get('https://xuangu.eastmoney.com/')
    time.sleep(3)
    for item in item_set:
        driver.find_element(By.CLASS_NAME, 'el-textarea__inner')  # 这里的name或id取决于实际网站的搜索框属性
        driver.find_element(By.CLASS_NAME, 'el-textarea__inner').send_keys(Keys.CONTROL, 'a')
        driver.find_element(By.CLASS_NAME, 'el-textarea__inner').send_keys(item)
        time.sleep(1)
        try:
            inputHintWrap = driver.find_element(By.CLASS_NAME, 'inputHintWrap')  # CSS选择器根据实际网站调整
            search_hint_list = inputHintWrap.find_elements(By.CLASS_NAME, 'searchHint')
            with open(current_dir + '/output.txt', 'a', encoding='utf-8') as file:
                for search_hint in search_hint_list:
                    try:
                        hint_title = search_hint.find_element(By.CLASS_NAME, 'hintTitle')
                        file.write(hint_title.text + '\n')
                        print(hint_title.text)
                    except Exception as e:
                        print(f"Error processing hint: {str(e)}")
            # suggestions_list = suggestions.find_elements(By.TAG_NAME, 'li')
            # # print(suggestions_list)
            # # 打开一个文件用于写入，如果文件不存在则创建它
            # # with open(current_dir + '/output.txt', 'a', encoding='utf-8') as file:
            # for suggestion in suggestions_list:
            #     print(suggestion.text)
            #         # 写入每一项suggestion.text到文件中，每项内容后面跟一个换行符
            #         # file.write(suggestion.text + '\n')
        except Exception as e:
            print(f"Error:{e}")
    # 关闭浏览器和服务
    driver.quit()
    service.stop()


if __name__ == '__main__':
    # 读取实体名词列表
    file_path = current_dir + '/11.txt'
    data_set = set()
    with open(file_path, 'r', encoding='UTF-8') as file:
        for line in file:
            line = line.strip()
            data_set.add(line)
    print(len(data_set))
    service = Service(driver_path)
    service.start()
    # 创建WebDriver实例
    driver = webdriver.Edge(service=service)

    # 问财
    # WenCai_WebSite(data_set)
    DongFang_WebSite(data_set)
    print("写入完成")
