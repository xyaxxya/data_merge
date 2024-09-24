import os
import json
import csv
import pandas as pd
import itertools

folder_path = './'
output_csv = 'output.csv'
is_txt_header = True
all_rows = []
base_fields = []
processed_files = set()
not_extracted_files = []


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


def check_additional_fields(current_fields):
    global base_fields
    if current_fields is None:
        return
    additional_fields = [field for field in current_fields if field not in base_fields]
    if additional_fields:
        print(f' 发现新字段{additional_fields}')
        include_fields = input(f" 是否将字段 [{', '.join(additional_fields)}] 包含到CSV中？(y/n): ").lower()
        if include_fields == 'y':
            base_fields.extend(additional_fields)
            base_fields.sort()


def process_file(file_path, file_type):
    global base_fields, all_rows

    if file_type == '.csv':
        with open(file_path, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            check_additional_fields(reader.fieldnames)
            for row in reader:
                all_rows.append([row.get(field, '') for field in base_fields])
        print(f"CSV 文件 {file_path} 提取完毕")
    elif file_type in ['.xlsx', '.xls', '.xlsm']:
        try:
            df = pd.read_excel(file_path)
            current_fields = df.columns.tolist()
            check_additional_fields(current_fields)
            for index, row in df.iterrows():
                all_rows.append([row.get(field, '') for field in base_fields])
        except Exception as e:
            print(f"读取Excel文件时出错: {e}")
        print(f"Excel 文件 {file_path} 提取完毕")
    elif file_type == '.json':
        with open(file_path, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
            if isinstance(data, list):
                check_additional_fields(data[0].keys())
                for entry in data:
                    all_rows.append([entry.get(field, '') for field in base_fields])
            elif isinstance(data, dict):
                check_additional_fields(data.keys())
                all_rows.append([data.get(field, '') for field in base_fields])
        print(f"JSON 文件 {file_path} 提取完毕")
    elif file_type == '.sql':
        with open(file_path, 'r', encoding='utf-8') as infile:
            sql_lines = infile.readlines()
            for line in sql_lines:
                if line.strip().lower().startswith("insert into"):
                    values_part = line.split("VALUES")[1].strip().strip("();")
                    values = [v.strip().strip("'") for v in values_part.split(',')]
                    all_rows.append(
                        [values[i] if i < len(values) else '' for i in range(len(base_fields))])
        print(f"SQL 文件 {file_path} 提取完毕")
    elif file_type == '.txt':
        with open(file_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
            header_handled = False
            for row in lines:
                fields = [item.strip() for item in row.strip().split('\t')]
                if not any(fields):
                    continue
                if not header_handled and is_txt_header:
                    if base_fields == []:
                        base_fields = fields
                    else:
                        check_additional_fields(fields)
                    header_handled = True
                else:
                    fields = [field if field else '' for field in fields]
                    fields = list(itertools.zip_longest(*[fields], fillvalue=''))[:len(base_fields)]
                    all_rows.append(fields)
        print(f"TXT 文件 {file_path} 提取完毕")


def process_files():
    global base_fields, all_rows, processed_files, not_extracted_files

    file_types = ['.csv', '.xlsx', '.json', '.sql', '.txt', '.xls', '.xlsm']

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    for filename in sorted(files):
        current_file_path = os.path.join(folder_path, filename)
        file_type = os.path.splitext(filename)[1]

        if filename.endswith(tuple(file_types)):
            processed_files.add(current_file_path)
            print(f'当前提取文件{filename}... ')
            process_file(current_file_path, file_type)
        else:
            not_extracted_files.append(filename)


def write_to_csv():
    global base_fields, all_rows
    all_rows = [row for row in all_rows if any(row)]
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as csvfile:
        csv_writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(base_fields)
        csv_writer.writerows(all_rows)


if __name__ == '__main__':
    print_logo()
    process_files()
    write_to_csv()
    print('Done~ ')
    print("未提取的文件 ：", list(set(not_extracted_files)))
