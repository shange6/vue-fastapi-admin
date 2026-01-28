import os
import subprocess
import re

def convert_dwg_to_dxf_with_chinese(input_dwg, output_dir):
    """
    封装 ODA 转换，并修复转换后的韩文乱码问题
    """
    if not os.path.exists(input_dwg):
        print(f"❌ 错误：找不到文件 {input_dwg}")
        return None

    os.makedirs(output_dir, exist_ok=True)
    input_dir = os.path.dirname(os.path.abspath(input_dwg))
    file_name = os.path.basename(input_dwg)
    output_dxf_path = os.path.join(output_dir, file_name.replace(".dwg", ".dxf"))

    # 1. 强制环境变量
    env = os.environ.copy()
    env["LC_ALL"] = "zh_CN.UTF-8"
    env["LANG"] = "zh_CN.UTF-8"

    # 2. 执行转换 (建议使用 ACAD2000 或 2004，这两个版本对中文字符集极其稳固)
    cmd = [
        "xvfb-run", "-a", "ODAFileConverter",
        input_dir,
        output_dir,
        "ACAD2004", "DXF", "0", "1", file_name
    ]

    print(f"正在转换并修复编码: {file_name} ...")
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True)
        
        # if os.path.exists(output_dxf_path):
        #     # --- 核心补丁：手动修正 DXF 文件的代码页标记 ---
        #     fix_dxf_codepage(output_dxf_path)
        #     print(f"✅ 转换并修复成功: {output_dxf_path}")
        #     return output_dxf_path
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换失败: {e.stderr.decode()}")
    
    return None

def fix_dxf_codepage(dxf_path):
    """
    暴力修复：将 DXF Header 中的代码页强制改为中国简体中文 (ANSI_936)
    """
    try:
        # 读取文件内容 (通常 DXF 是文本格式)
        with open(dxf_path, 'r', encoding='ascii', errors='ignore') as f:
            content = f.read()

        # 1. 查找 $DWGCODEPAGE 并将其后的值改为 ANSI_936
        # DXF 格式中，$DWGCODEPAGE 后面通常跟着 3 (组码), 然后是编码名
        new_content = re.sub(
            r'(\$DWGCODEPAGE\s+3\s+)\w+', 
            r'\1ANSI_936', 
            content, 
            flags=re.MULTILINE
        )

        # 2. 检查并添加或修改 $SYSCODEPAGE
        if '$SYSCODEPAGE' in new_content:
            new_content = re.sub(
                r'(\$SYSCODEPAGE\s+3\s+)\w+', 
                r'\1ANSI_936', 
                new_content, 
                flags=re.MULTILINE
            )

        # 写回文件
        with open(dxf_path, 'w', encoding='ascii') as f:
            f.write(new_content)
            
    except Exception as e:
        print(f"⚠️ 编码补丁执行失败: {e}")

def clean_cad_chinese(text):
    """
    专门解析 DXF 内部的汉字转义（处理 \M+5XXXX 格式）
    """
    if not text: return ""
    
    # 处理天河/天正等插件特有的 \M+5XXXX 格式
    pattern = re.compile(r'\\[Mm]\+5([0-9A-Fa-f]{4})')
    def replace_hex(match):
        try:
            return binascii.unhexlify(match.group(1)).decode('gbk')
        except:
            return match.group(0)
            
    text = pattern.sub(replace_hex, text)
    # 移除 MText 的格式符，如 \P (换行), \fSimSun; (字体) 等
    text = re.sub(r'\\[fFhHwWkK].*?;|[{}]|\\P', ' ', text)
    return text.strip()


def extract_blocks_to_list(dxf_path):
    """
    深度遍历 DXF，以汉字解析方式提取数据
    """
    print("xxxxxxxxxxxxxxxxxxxxxx")
    doc = ezdxf.readfile(dxf_path)
    print(doc)
    all_data = []

    # 深度遍历模型空间中的 INSERT (块)
    for insert in doc.modelspace().query("INSERT"):
        block_name = insert.dxf.name
        block_content = []

        # 1. 提取属性文字 (ATTRIB)
        for attr in insert.attribs:
            clean_val = clean_cad_chinese(attr.dxf.text)
            if clean_val:
                block_content.append({'x': attr.dxf.insert.x, 'y': attr.dxf.insert.y, 'text': clean_val})

        # 2. 提取块定义内部文字
        block_def = doc.blocks.get(block_name)
        if block_def:
            for e in block_def.query("TEXT MTEXT"):
                content = clean_cad_chinese(e.dxf.text if e.dxftype() == 'TEXT' else e.text)
                if content:
                    block_content.append({'x': e.dxf.insert.x, 'y': e.dxf.insert.y, 'text': content})
        
        if block_content:
            all_data.append({"block_name": block_name, "data": block_content})
            
    return all_data

# --- 执行流程 ---
if __name__ == "__main__":
    DWG_PATH = "/mnt/c/Users/panzheng/Desktop/1/横向移动车.dwg"
    OUT_DIR = "/home/panzheng/dwg/output_dxf"

    # 第一步：转换 (带汉字环境补丁)
    dxf_file = convert_dwg_to_dxf_with_chinese(DWG_PATH, OUT_DIR)
    exit()
    # 第二步：解析并显示（或后续保存 Excel）
    if dxf_file:
        results = extract_blocks_to_list(dxf_file)
        for item in results:
            print(f"块 [{item['block_name']}] 提取到文字: {[d['text'] for d in item['data'][:3]]}...")