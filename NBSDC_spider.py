# -*- coding: utf-8 -*-

"""
2018年统计用区划代码和城乡划分代码提取Python代码

从国家统计局2018年统计用区划代码和城乡划分代码(截止2018年10月31日)网页提取全国各省市的代码，并且以JSON格式存储 http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/index.html

存储后的JSON文件，可以直接以mongoimport的方式导入到mongodb的一个collection内

json的每个entry保留了partent节点的代码，可以在程序内重新构建树状层级关系

当前环境使用Python 3.6，在执行本程序前请对相应变量进行更改。

部分代码参考了网上的示例代码，如有侵权请创建issue联系本人。

Mongoimport 示例，windows:
mongoimport /host:<yourhost> /port:<port> /username:<name> /password:<password> /db:<db> /collection:<coll> /drop /file:"<your_json_file>"


"""
import os
import re
import requests
import time
from NBS_Item import nbsItem

'''
根据需要，做相应的更新
'''
output_root_dir = 'c:/temp/data/'  # 数据储存路径，注意以 / 结尾
url = r'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/index.html'  # 初始URL
url_base = r'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/'  # base url

result1 = []  # 省
result2 = []  # 市
result3 = []  # 区/县
result4 = []  # 街道
result5 = []  # 村

kv = {'user-agent': 'Mozilla/5.0'}
n = 0

r = requests.get(url, headers=kv)
r.raise_for_status()
r.encoding = r.apparent_encoding
pattern = re.compile("<a href='(.*?)'>(.*?)<")  # 正则表达式
result1 = list(set(re.findall(pattern, r.text)))  # 从主页面获取子页面的html
print('result1')
print(result1)
i2 = 0

if not os.path.isdir(output_root_dir):
    os.makedirs(output_root_dir)
    print("已创建目录:"+output_root_dir)

def append_to_json(json_file, nbsItem):
    output_file = output_root_dir + json_file
    with open(output_file, 'a', encoding='utf-8')as file_object:
        # json.dump(nbsItem, file_object, default=lambda obj: obj.__dict__, indent=4, ensure_ascii=False)
        file_object.write(nbsItem.to_json_str())


cur_parent = '100000000000'  # 国家
cur_province = ""
cur_city = ""
cur_county = ""
cur_village = ""

for i1a in result1:
    try:
        url2a = i1a[0]
        cur_name = i1a[1]  # 一级地址

        #如果只想导出某个省份的数据，可以在这里添加过滤
        #if url2a.find(r'11.html') == -1:
        #    continue

        cur_id = url2a[0:2] + '0000000000'  # 省级代码是前两位，后面填0
        cur_province = cur_name
        # 每个省保存一个json文件
        jsonfile = cur_province+"_"+cur_id + '.json'
        print("正在导出[" + cur_province + "]相关数据到目标文件："+jsonfile)

        url2 = url_base + url2a

        r2 = requests.get(url2, headers=kv)
        r2.raise_for_status()
        r2.encoding = r2.apparent_encoding
        # 爬取当前页面的文字信息，形成新的NBS_Item
        newItem = nbsItem()
        newItem._id = cur_id
        newItem.name = cur_name
        newItem.parent = cur_parent
        newItem.fullname = cur_province
        # 提取下一级的相关信息，正则表达式提取目标字段
        pattern2 = re.compile("class='citytr'><td><a href='(.*?)'>(.*?)</a></td><td><a href='(.*?)'>(.*?)</a>")
        result2 = list(set(re.findall(pattern2, r2.text)))
        for i2a in result2:  # 爬取的城市信息和城市代码混在一起，需要将代码清除
            newChild = {
                "areaCode": "",
                "_id": str(i2a[1]),
                "name": i2a[3],
                "fullname": cur_province + i2a[3]
            }
            newItem.items.append(newChild)

        # 写入json文件
        append_to_json(jsonfile, newItem)

    except:
        print('省级数据处理错误! 程序退出！ ')
        exit(1)
    # cur_l1_parent 省一级的ID
    cur_l1_parent = cur_id
    # 解析地级市一级的数据
    for city in result2:
        try:
            cityItem = nbsItem()
            url3a = city[0]
            cur_id = str(city[1])
            cur_name = city[3]
            cur_city = cur_name
            cityItem.name = cur_name
            cityItem._id = cur_id
            cityItem.parent = cur_l1_parent
            cityItem.fullname = cur_province + cur_city
            url3 = url_base + url3a
            # 获取下一级区县信息
            r3 = requests.get(url3, headers=kv)
            r3.raise_for_status()
            r3.encoding = r3.apparent_encoding
            pattern3 = re.compile("class='countytr'><td><a href='(.*?)'>(.*?)</a></td><td><a href='(.*?)'>(.*?)</a>")
            result3 = list(set(re.findall(pattern3, r3.text)))
            for i3a in result3:  # 爬取的城市信息和城市代码混在一起，需要将代码清除
                newCityChild = {
                    "areaCode": "",
                    "_id": str(i3a[1]),
                    "name": i3a[3],
                    "fullname": cur_province + cur_city + i3a[3]
                }
                cityItem.items.append(newCityChild)
            # 特殊处理，市一级会出现不带链接的“市辖区”，需要特殊处理
            pattern3 = re.compile("class='countytr'><td>(\d+)</td><td>(.*?)</td>")
            result3a = list(set(re.findall(pattern3, r3.text)))
            for i3a in result3a:  # 爬取的城市信息和城市代码混在一起，需要将代码清除
                newCityChild = {
                    "areaCode": "",
                    "_id": str(i3a[0]),
                    "name": i3a[1],
                    "fullname": cur_province + cur_city + i3a[1]
                }
                cityItem.items.append(newCityChild)
            # 写入json文件
            append_to_json(jsonfile, cityItem)
        except:
            print('市级数据处理错误! 程序退出！ ')
            exit(1)

        # 进入区县级别数据获取
        # cur_l2_parent 市一级的id
        cur_l2_parent = cur_id
        for county in result3:
            try:
                countyItem = nbsItem()
                url4a = county[0]
                cur_id = str(county[1])
                cur_name = county[3]
                cur_county = cur_name
                countyItem.name = cur_name
                countyItem._id = cur_id
                countyItem.parent = cur_l2_parent
                countyItem.fullname = cur_province + cur_city + cur_county
                url4 = url_base + url4a[3:5] + '/' + url4a

                r4 = requests.get(url4, headers=kv)
                r4.raise_for_status()
                r4.encoding = r4.apparent_encoding
                pattern4 = re.compile("class='towntr'><td><a href='(.*?)'>(.*?)</a></td><td><a href='(.*?)'>(.*?)</a>")
                result4 = list(set(re.findall(pattern4, r4.text)))
                for i4a in result4:  # 爬取的城市信息和城市代码混在一起，需要将代码清除
                    newCountyChild = {
                        "areaCode": "",
                        "_id": str(i4a[1]),
                        "name": i4a[3],
                        "fullname": cur_province + cur_city + cur_county + i4a[3]
                    }
                    countyItem.items.append(newCountyChild)
                # 写入json文件
                append_to_json(jsonfile, countyItem)
            except:
                print('区县级数据处理错误! 程序退出！ ')
                exit(1)

            # 下一级，村一级数据
            # cur_l3_parent 街道、乡镇一级的ID
            cur_l3_parent = cur_id
            for village in result4:
                try:
                    villageItem = nbsItem()
                    url5a = village[0]
                    cur_id = str(village[1])
                    cur_name = village[3]
                    cur_village = cur_name
                    villageItem.name = cur_name
                    villageItem._id = cur_id
                    villageItem.parent = cur_l3_parent
                    villageItem.fullname = cur_province + cur_city + cur_county + cur_village
                    url5 = url_base + cur_id[0:2] + '/' + cur_id[2:4] + '/' + url5a

                    r5 = requests.get(url5, headers=kv)
                    r5.raise_for_status()
                    r5.encoding = r5.apparent_encoding
                    pattern5 = re.compile("class='villagetr'><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td>")
                    result5 = list(set(re.findall(pattern5, r5.text)))
                    for i5a in result5:  # 爬取的城市信息和城市代码混在一起，需要将代码清除
                        newVillageChild = {
                            "areaCode": "",
                            "_id": str(i5a[0]),
                            "name": i5a[2],
                            "fullname": cur_province + cur_city + cur_county + cur_village + i5a[2]
                        }
                        villageItem.items.append(newVillageChild)
                    # 写入json文件
                    append_to_json(jsonfile, villageItem)
                except:
                    print('乡镇、街道级数据处理错误! 程序退出！ ')
                    exit(1)
    print("已完成导出[" + cur_province + "]相关数据到目标文件：" + jsonfile)
print('已完成，程序结束！')
