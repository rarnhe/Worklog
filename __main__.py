import json
import os
from openpyxl import Workbook, load_workbook

def parse_line(line):
    """解析单行数据，返回 (第一字符串, 日期, 时间, 时长数值) 或 None"""
    line = line.strip()
    if not line:
        return None
    
    try:
        line = line.replace('"', '"').replace('"', '"')
        data = json.loads(line)
        
        if not data:
            return None
        
        first_key = list(data.keys())[0]
        
        if not first_key or first_key.strip() == '':
            return None
        
        value = data[first_key]
        parts = value.split(',')
        if len(parts) != 2:
            return None
        
        date_time_str = parts[0].strip()
        duration_str = parts[1].strip()
        
        date_part, time_part = split_datetime(date_time_str)
        hours = convert_duration(duration_str)
        
        return (first_key, date_part, time_part, hours)
    
    except:
        return None

def split_datetime(date_time_str):
    """将 '2026年7月29日 17:45' 拆分为 '2026-07-29' 和 '17:45'"""
    try:
        cleaned = date_time_str.replace('年', '-').replace('月', '-').replace('日', '')
        
        if ' ' in cleaned:
            date_part, time_part = cleaned.split(' ', 1)
            date_parts = date_part.split('-')
            if len(date_parts) == 3:
                year = date_parts[0].strip()
                month = date_parts[1].strip().zfill(2)
                day = date_parts[2].strip().zfill(2)
                date_formatted = f"{year}-{month}-{day}"
            else:
                date_formatted = date_part
            
            time_parts = time_part.split(':')
            if len(time_parts) >= 2:
                hour = time_parts[0].strip().zfill(2)
                minute = time_parts[1].strip().zfill(2)
                time_formatted = f"{hour}:{minute}"
            else:
                time_formatted = time_part
            
            return date_formatted, time_formatted
        else:
            return date_time_str, "00:00"
    except:
        return date_time_str, "00:00"

def convert_duration(duration_str):
    """将 '2:00:00' 转换为小时数"""
    try:
        parts = duration_str.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            total_hours = hours + minutes/60 + seconds/3600
            if total_hours == int(total_hours):
                return int(total_hours)
            else:
                return round(total_hours, 1)
    except:
        return 0

def get_excel_path():
    """获取与py文件同名的xlsx文件路径"""
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    script_name = "Worklog"
    excel_path = os.path.join(script_dir, "Worklog.xlsx")
    return excel_path, script_name

def is_duplicate(ws, row_data):
    """检查前四列内容是否完全一致"""
    if ws.max_row <= 1:
        return False
    
    for row in range(2, ws.max_row + 1):
        match = True
        for col in range(1, 5):
            existing_value = ws.cell(row=row, column=col).value
            new_value = row_data[col-1]
            if isinstance(existing_value, (int, float)) and isinstance(new_value, (int, float)):
                if abs(existing_value - new_value) > 0.001:
                    match = False
                    break
            elif existing_value != new_value:
                match = False
                break
        
        if match:
            return True
    
    return False

def find_first_empty_row(ws):
    """找到第一行A列为空的行（从第2行开始）"""
    row = 2
    while True:
        cell_value = ws.cell(row=row, column=1).value
        if cell_value is None or str(cell_value).strip() == '':
            return row
        row += 1
        if row > 100000:
            break
    return ws.max_row + 1

def process_data(lines, excel_path, sheet_name):
    """处理数据并写入Excel"""
    # 解析数据
    parsed_data = []
    failed_count = 0
    
    for line in lines:
        if not line or line.strip() == '':
            continue
        
        result = parse_line(line)
        if result is None:
            failed_count += 1
            continue
        
        parsed_data.append(result)
    
    if not parsed_data:
        print(f"⚠️ 无有效数据 (失败: {failed_count})")
        return
    
    # 加载或创建Excel
    try:
        if os.path.exists(excel_path):
            wb = load_workbook(excel_path)
        else:
            wb = Workbook()
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
    except PermissionError:
        print("❌ 文件被占用，请关闭Excel文件")
        return
    
    # 获取或创建sheet
    if sheet_name not in wb.sheetnames:
        ws = wb.create_sheet(sheet_name)
        headers = ["任务名称", "日期", "时间", "小时数"]
        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)
    else:
        ws = wb[sheet_name]
    
    # 写入数据
    success_count = 0
    duplicate_count = 0
    
    for row_data in parsed_data:
        if is_duplicate(ws, row_data):
            duplicate_count += 1
            continue
        
        target_row = find_first_empty_row(ws)
        for col_idx, value in enumerate(row_data, 1):
            ws.cell(row=target_row, column=col_idx, value=value)
        success_count += 1
    
    # 保存
    if success_count > 0:
        try:
            wb.save(excel_path)
            print(f"✅ 写入 {success_count} 条" + (f" (跳过 {duplicate_count} 条重复)" if duplicate_count > 0 else "") + (f" | 失败 {failed_count} 条" if failed_count > 0 else ""))
        except PermissionError:
            print("❌ 保存失败：文件被占用，请关闭Excel文件")
    else:
        print(f"⚠️ 无新数据写入" + (f" (重复 {duplicate_count} 条)" if duplicate_count > 0 else "") + (f" | 失败 {failed_count} 条" if failed_count > 0 else ""))

def show_prompt(excel_path, sheet_name):
    """显示输入提示"""
    print()
    print(f"📁 {os.path.basename(excel_path)} → {sheet_name}")
    print("-" * 50)
    print("粘贴数据 (每行一条)，空行执行，'exit'退出")
    print("-" * 50)

def main():
    excel_path, sheet_name = get_excel_path()
    
    show_prompt(excel_path, sheet_name)
    
    while True:
        lines = []
        while True:
            try:
                line = input()
                if line.strip().lower() == 'exit':
                    print("👋 退出")
                    return
                if line == '' and len(lines) > 0:
                    break
                lines.append(line)
            except KeyboardInterrupt:
                print("\n👋 退出")
                return
            except EOFError:
                print("\n👋 退出")
                return
        
        if lines:
            process_data(lines, excel_path, sheet_name)
        
        # 每次处理完一轮后重新显示提示
        show_prompt(excel_path, sheet_name)

if __name__ == "__main__":
    main()