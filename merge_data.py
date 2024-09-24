import os
import json
import csv
import pandas as pd

folder_path = './'
output_csv = 'xxxx.csv'
is_txt_header = True  # 默认为 True 表示第一行为标题
all_rows = []  # 存储所有文件的数据行
base_fields = []  # 存储基础字段
base_file = None  # 存储基础文件名
processed_files = set()  # 用于存储已处理文件的集合
not_extracted_files = []  # 用于记录未提取的文件

def print_logo():
    logo = '''
    _____.___..___ _____.___..___        
    \__  |   ||   |\__  |   ||   |       
     /   |   ||   | /   |   ||   |       
     \____   ||   | \____   ||   |       
     / ______||___| / ______||___| ______
     \/             \/            /_____/
     '''
    print(logo)

def get_base_fields():
    global base_fields, base_file
    files = [f for f in os.listdir(folder_path) if f.endswith(('.csv', '.json', '.xlsx', '.xls', '.sql', '.txt'))]

    if not files:
        print("没有找到任何支持的文件。")
        return

    base_file = files[0]

    if base_file.endswith('.csv'):
        try:
            with open(os.path.join(folder_path, base_file), 'r', encoding='utf-8-sig') as infile:
                reader = csv.DictReader(infile)
                base_fields = reader.fieldnames
        except Exception as e:
            print(f"读取基础文件时出错: {e}")
    elif base_file.endswith('.json'):
        try:
            with open(os.path.join(folder_path, base_file), 'r', encoding='utf-8') as infile:
                data = json.load(infile)
                if isinstance(data, list):
                    base_fields = list(data[0].keys())
                elif isinstance(data, dict):
                    base_fields = list(data.keys())
        except Exception as e:
            print(f"读取基础文件时出错: {e}")

def check_additional_fields(current_fields):
    global base_fields
    if current_fields is None:
        return
    additional_fields = [field for field in current_fields if field not in base_fields]
    if additional_fields:
        print(f'🤣发现新字段{additional_fields}')
        include_fields = input(f"😊是否将字段 [{', '.join(additional_fields)}] 包含到CSV中？(y/n): ").lower()
        if include_fields == 'y':
            base_fields.extend(additional_fields)

def process_files():
    global base_fields, all_rows, base_file, processed_files, not_extracted_files

    file_types = ['.csv', '.xlsx', '.json', '.sql', '.txt', '.xls', '.xlsm']

    base_file_path = os.path.join(folder_path, base_file)

    for file_type in file_types:
        print(f"💥正在提取 {file_type} 文件...")
        for filename in sorted(os.listdir(folder_path)):
            current_file_path = os.path.join(folder_path, filename)
            if current_file_path in processed_files or current_file_path == base_file_path:
                continue  # 跳过基础文件和已处理的文件

            if filename.endswith(file_type):
                processed_files.add(current_file_path)
                print(f'当前提取文件{filename}...💟')
                if file_type == '.csv':
                    with open(current_file_path, 'r', encoding='utf-8-sig') as infile:
                        reader = csv.DictReader(infile)
                        check_additional_fields(reader.fieldnames)
                        for row in reader:
                            all_rows.append([row.get(field, '') for field in base_fields])
                    print(f"CSV 文件 {filename} 提取完毕")
                elif file_type in ['.xlsx', '.xls', '.xlsm']:
                    try:
                        df = pd.read_excel(current_file_path)
                        current_fields = df.columns.tolist()
                        check_additional_fields(current_fields)
                        for index, row in df.iterrows():
                            all_rows.append([row.get(field, '') for field in base_fields])
                    except Exception as e:
                        print(f"读取Excel文件时出错: {e}")
                    print(f"Excel 文件 {filename} 提取完毕")
                elif file_type == '.json':
                    with open(current_file_path, 'r', encoding='utf-8') as infile:
                        data = json.load(infile)
                        if isinstance(data, list):
                            check_additional_fields(data[0].keys())
                            for entry in data:
                                all_rows.append([entry.get(field, '') for field in base_fields])
                        elif isinstance(data, dict):
                            check_additional_fields(data.keys())
                            all_rows.append([data.get(field, '') for field in base_fields])
                    print(f"JSON 文件 {filename} 提取完毕")
                elif file_type == '.sql':
                    with open(current_file_path, 'r', encoding='utf-8') as infile:
                        sql_lines = infile.readlines()
                        for line in sql_lines:
                            if line.strip().lower().startswith("insert into"):
                                values_part = line.split("VALUES")[1].strip().strip("();")
                                values = [v.strip().strip("'") for v in values_part.split(',')]
                                all_rows.append(
                                    [values[i] if i < len(values) else '' for i in range(len(base_fields))])
                    print(f"SQL 文件 {filename} 提取完毕")
                elif file_type == '.txt':
                    with open(current_file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        header_handled = False
                        for row in lines:
                            fields = [item.strip() for item in row.strip().split('\t')]
                            if not header_handled and is_txt_header:
                                if base_fields == []:
                                    base_fields = fields
                                else:
                                    check_additional_fields(fields)
                                header_handled = True
                            else:
                                all_rows.append(fields)
                    print(f"TXT 文件 {filename} 提取完毕")
            else:
                not_extracted_files.append(filename)

def write_to_csv():
    global base_fields, all_rows
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(base_fields)
        csv_writer.writerows(all_rows)

if __name__ == '__main__':
    print_logo()
    get_base_fields()
    process_files()
    write_to_csv()
    print('Done~😍')
    print("未提取的文件❌：", list(set(not_extracted_files)))

