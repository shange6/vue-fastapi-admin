def iterative_kv_parser(text, keywords):
    """
    不使用 re 模块，通过关键字迭代切分字符串
    :param text: 原始长字符串
    :param keywords: 关键字列表，例如 ["项目名称：", "合同号："]
    :return: 提取后的字典
    """
    # 1. 查找所有关键字在字符串中的起始位置
    found_segments = []
    for k in keywords:
        pos = text.find(k)
        if pos != -1:
            found_segments.append({"key": k, "start": pos})

    # 2. 按照在字符串中出现的先后顺序排序（防止输入的 keywords 顺序不对）
    found_segments.sort(key=lambda x: x["start"])

    result = {}
    
    # 3. 核心迭代逻辑：利用当前关键字和下一个关键字的位置进行切片
    for i in range(len(found_segments)):
        current = found_segments[i]
        key_name = current["key"]
        
        # 内容的起点 = 当前关键字的起始位置 + 关键字本身的长度
        val_start = current["start"] + len(key_name)
        
        # 内容的终点 = 下一个关键字的起始位置（如果是最后一个，则到字符串末尾）
        if i + 1 < len(found_segments):
            val_end = found_segments[i + 1]["start"]
        else:
            val_end = len(text)
        
        # 提取并清洗数据
        raw_val = text[val_start:val_end]
        # 清除常见的 CAD 格式干扰项
        clean_val = raw_val.replace("\\P", " ").strip()
        
        # 去掉冒号作为字典的 Key
        result[key_name.strip("：: ")] = clean_val
        
    return result

# --- 测试代码 ---
raw_data = "项目名称：曲阜东宏3620钢管防腐铺机 合同号：WS24-19部件名称：横向移动车 数量：1"
target_keys = ["项目名称：", "合同号：", "部件名称：", "数量："]

data_dict = iterative_kv_parser(raw_data, target_keys)
print(data_dict)