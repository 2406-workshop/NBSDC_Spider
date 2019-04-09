#!-*-coding:UTF-8-*-
class nbsItem(object):
    _id = 0
    name = ""
    parent = 0
    items = []
    fullname = ""

    def __init__(self):
        self._id = 0
        self.name = ""
        self.parent = 0
        self.items = []
        self.fullname = ''

    def to_json_str(self):
        ret_str = '{\n\t' + '"_id" : ' + str(self._id) + ','
        ret_str += '\n\t' + '"name" : "' + self.name + '"' + ','
        ret_str += '\n\t' + '"fullname" : "' + self.fullname + '"' + ','
        ret_str += '\n\t' + '"parent" : ' + str(self.parent) + ','
        ret_str += '\n\t' + '"items" : ['
        idx = 0
        for item in self.items:
            ret_str += '\n\t\t{'
            ret_str += '\n\t\t\t' + '"_id": ' + str(item["_id"]) + ','
            ret_str += '\n\t\t\t' + '"name": "' + str(item["name"]) + '"' + ','
            ret_str += '\n\t\t\t' + '"fullname": "' + str(item["fullname"]) + '"' + ','
            ret_str += '\n\t\t\t' + '"areaCode":""'
            ret_str += '\n\t\t}'
            idx += 1
            if (idx < len(self.items)):
                ret_str += ','

        ret_str += '\n\t' + ']'
        ret_str += '\n' + '}\n'
        return ret_str
