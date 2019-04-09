# NBSDC_Spider
2018年统计用区划代码和城乡划分代码提取Python代码

从国家统计局2018年统计用区划代码和城乡划分代码(截止2018年10月31日)网页提取全国各省市的代码，并且以JSON格式存储
http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2018/index.html 


存储后的JSON文件，可以直接以mongoimport的方式导入到mongodb的一个collection内


json的每个entry保留了partent节点的代码，可以在程序内重新构建树状层级关系
