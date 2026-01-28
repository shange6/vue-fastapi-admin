import ezdxf
import re
import binascii


dxf_path = "/mnt/c/Users/panzheng/Desktop/1/1.dxf"
# 打开DXF文件
doc = ezdxf.readfile(dxf_path)
# 获取模型空间
msp = doc.modelspace()

pattern_blank = re.compile(r"\s+")
pattern_format = re.compile(r'\\[fFhHwWkK].*?;|[{}]|\\P')
pattern_m5 = re.compile(r'\\[Mm]\+5([0-9A-Fa-f]{4})')
pattern_unicode = re.compile(r'\\[Uu]\+?([0-9A-Fa-f]{4})')

def replace_hex(match: re.match):
    try:
        if match.re == pattern_m5:  # 替换天河/天正格式
            return binascii.unhexlify(match.group(1)).decode('gbk')
        if match.re == pattern_unicode: # 替换unicode格式
            return chr(int(match.group(1), 16))
    except:
        return match.group(0)

def replace_sub(text: str) -> str:
    text = pattern_m5.sub(replace_hex, text)
    text = pattern_unicode.sub(replace_hex, text)
    text = pattern_format.sub("", text)
    text = pattern_blank.sub("", text)
    return text
# project_info_dict = {}
# project_info_list = ["项目名称", "合同号", "部件名称" ,"部件数量", "数量"]

# def check_text(
#         key: str, 
#         value: str, 
#         project_info_dict: dict,
#         project_info_list: list
#     ) -> dict:
    
#     print(f"1==>key={key}, value={value}")
#     for key1 in project_info_list:
#         if key1 in value:
#             print(f"2==>key={key}, key1={key1}, value={value}")
#             project_info_dict[key1] = value.split(key1)[1]#.replace("：", "")
#             # print(f"key1={key1}, value.split(key1)[1]={value.split(key1)[1]}")            
#             print("3==>",project_info_dict)
#             if key:
#                 project_info_dict[key] =  value.split(key1)[0]
#                 print(f"4==>key={key}, value.split(key1)[0]={value.split(key1)[0]}")
#             # else:
#             #     project_info_dict[key1] = 
#             # print(f"4==>key={key}")
#             return check_text(key1, project_info_dict[key1], project_info_dict, project_info_list)
    #     else:
    #         dict1[key1] =  value
    #         # return dict1
    # print(dict1)
    # return dict1

project_info = {}
project_info_keys = ["项目名称", "合同号", "部件名称" ,"部件数量", "数量"]
def check_text(         # 把value拆分成{key: value}的格式，结果保存在project_info: dict中
        key: str,       # key是project_info_keys中的一个，当前没有传None
        value: str,     # key值对应的value，当前没有传要分析的字符串
        project_info: dict,     # 保存结果的字典
        project_info_keys: list # value中可能出现key
    ):
    for key1 in project_info_keys:
        if key1 in value:   # 字符串中包含key1
            project_info[key1] = value.split(key1)[1]   # 添加字典项目key1：value1
            if key: # key是value的关键字，也就是上次循环的key1值
                # 如果value中包含一个key1，则说明value不是单纯的value,还包含了另一个key:value
                # 修改上次循环的key:value值, 去掉key1:value1
                project_info[key] =  value.split(key1)[0].replace("：", "") 
            # 把value去掉value1后的部分传给自己，做迭代运算
            return check_text(key1, project_info[key1], project_info, project_info_keys)

# 1. 查询所有块引用INSERT
insert_list = msp.query("MTEXT")
print(len(insert_list))
for insert in insert_list:
    # text = pattern_m5.sub(replace_hex, insert.dxf.text)
    # # text = replace_sub(insert.dxf.text)
    # text = pattern_format.sub("", text)
    # text = pattern_blank.sub("", text)
    # print(text)
    # text = text.split("项目名称：")
    # print(insert.dxf.text)
    text = replace_sub(insert.dxf.text)
    # print(text)
    texts = text.split()
    for text in texts:
        # print(text)
    #     for s in list1:
    #         if s in text:
    #             newtext = text.split(s)[1]
    #             dict1[s] = newtext
    #             for v in list1:
    #                 if v in newtext:
    #                     dict1[v] = newtext.split(v)[1]
    #                     newtext2 = newtext.replace(v, "")
    #                     dict1[s] = newtext2.replace(dict1[v], "")
    # break
    # print(dict1)
        # for key in list1:
        check_text(None, text, project_info, project_info_keys)
        print(project_info)
    break


        

