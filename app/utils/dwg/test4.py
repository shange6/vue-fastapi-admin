import ezdxf
import re
import binascii
import pandas as pd
import os

class CADToExcelExporter:
    def __init__(self, dxf_path):
        if not os.path.exists(dxf_path):
            raise FileNotFoundError(f"找不到文件: {dxf_path}")
        self.doc = ezdxf.readfile(dxf_path)
        self.msp = self.doc.modelspace()
        self.all_tables = {} # 存储 {块名: [行数据列表]}

    def _decode(self, text):
        """处理 \M+5 编码及格式清洗"""
        if not text: return ""
        pattern = re.compile(r'\\[Mm]\+5([0-9A-Fa-f]{4})')
        def replace_hex(match):
            try: return binascii.unhexlify(match.group(1)).decode('gbk')
            except: return ""
        text = pattern.sub(replace_hex, text)
        # 清除 CAD 控制符和换行符
        text = re.sub(r'\\[hHwWfFkK].*?;|[{}]|\\P', ' ', text)
        return text.strip()

    def _convert_to_grid(self, elements, y_threshold=8.0):
        """将带有坐标的元素集合转换为有序的二维列表"""
        if not elements: return []
        
        # 1. 按 Y 轴降序排列 (从上到下)
        elements.sort(key=lambda e: e['y'], reverse=True)
        
        rows = []
        curr_row = [elements[0]]
        for i in range(1, len(elements)):
            if abs(elements[i]['y'] - curr_row[-1]['y']) <= y_threshold:
                curr_row.append(elements[i])
            else:
                rows.append(curr_row)
                curr_row = [elements[i]]
        rows.append(curr_row)

        # 2. 每一行按 X 轴升序排列 (从左到右)
        grid = []
        for row in rows:
            row.sort(key=lambda e: e['x'])
            # 提取文字并过滤重复内容
            row_content = []
            for item in row:
                if not row_content or item['text'] != row_content[-1]:
                    row_content.append(item['text'])
            grid.append(row_content)
        return grid

    def process_and_save(self, output_file="output.xlsx"):
        print("正在提取块数据...")
        
        for insert in self.msp.query("INSERT"):
            block_name = insert.dxf.name
            table_data = []

            # 策略 A: 提取属性 (ATTRIB) - 动态填充的内容
            if insert.attribs:
                attr_elements = [{'x': a.dxf.insert.x, 'y': a.dxf.insert.y, 'text': self._decode(a.dxf.text)} 
                                 for a in insert.attribs if self._decode(a.dxf.text)]
                table_data.extend(self._convert_to_grid(attr_elements))

            # 策略 B: 提取块定义内的静态文字 - 表头等
            block_def = self.doc.blocks.get(block_name)
            if block_def:
                static_elements = []
                for e in block_def.query("TEXT MTEXT"):
                    content = self._decode(e.dxf.text if e.dxftype() == 'TEXT' else e.text)
                    if content:
                        static_elements.append({'x': e.dxf.insert.x, 'y': e.dxf.insert.y, 'text': content})
                table_data.extend(self._convert_to_grid(static_elements))

            if table_data:
                # 避免 Sheet 名字冲突或过长
                sheet_key = re.sub(r'[\\/*?:\[\]]', '_', block_name)[:30]
                if sheet_key not in self.all_tables:
                    self.all_tables[sheet_key] = table_data

        # 使用 Pandas 写入 Excel
        if self.all_tables:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for sheet_name, data in self.all_tables.items():
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
            print(f"✅ 导出成功！文件名: {output_file}")
        else:
            print("❌ 未在块中发现任何有效的文字数据。")

if __name__ == "__main__":
    DXF_PATH = "/home/panzheng/dwg/output_dxf/横向移动车.dxf"
    exporter = CADToExcelExporter(DXF_PATH)
    exporter.process_and_save("横向移动车_数据提取.xlsx")