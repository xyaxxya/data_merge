import os
import pandas as pd
import json
import re


# JSON
def extract_json_fields(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list) and data:
            return list(data[0].keys()), pd.DataFrame(data)
        return list(data.keys()), pd.DataFrame([data])


# SQL
def extract_sql_fields(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        pattern = r'CREATE TABLE\s+\w+\s*\((.*?)\);'
        matches = re.findall(pattern, content, re.DOTALL)
        fields = []
        for match in matches:
            field_lines = match.split(',')
            for line in field_lines:
                field_name = line.strip().split()[0]
                fields.append(field_name)
        return fields, pd.DataFrame()  # 返回空数据框


# 文件读取
def read_file(file):
    ext = os.path.splitext(file)[1].lower()

    if ext == '.csv':
        df = pd.read_csv(file, encoding='utf-8')
        return df.columns.tolist(), df

    elif ext in ['.xlsx', '.xls', '.xlsm']:
        df = pd.read_excel(file)
        return df.columns.tolist(), df

    elif ext == '.json':
        return extract_json_fields(file)

    elif ext == '.sql':
        return extract_sql_fields(file)

    return None, None


def ask_yes_no(question):
    answer = input(question)
    return answer.lower() in ['y', 'yes', '']


def merge_files_to_csv():
    if os.path.isfile('output.csv'):
        if ask_yes_no("💥output.csv 文件已存在，是否删除它？ (y/n): "):
            os.remove('output.csv')
            print("❌output.csv 已被删除。")
        else:
            print("💟将保留现有的 output.csv 文件。")
            return

    categories = {
        'CSV': ['.csv'],
        'Excel': ['.xlsx', '.xls', '.xlsm'],
        'JSON': ['.json'],
        'SQL': ['.sql']
    }

    all_files = []

    # 分类
    for filename in os.listdir('.'):
        if os.path.isfile(filename):
            ext = os.path.splitext(filename)[1].lower()
            for category, extensions in categories.items():
                if ext in extensions:
                    all_files.append(filename)
                    break

    merged_data = {}
    field_names = []
    max_length = 0  # 追踪最长数据列

    for file in all_files:
        print(f"👾Reading file: {file}")
        fields, data = read_file(file)

        # 字段
        missing_fields = []
        for field in fields:
            if field not in field_names:
                missing_fields.append(field)

        if missing_fields:
            field_str = '、'.join(missing_fields)
            if ask_yes_no(f"💕Fields '{field_str}' not found in merged fields. Do you want to add them? (y/n): "):
                field_names.extend(missing_fields)
                for field in missing_fields:
                    merged_data[field] = []

        # 长度一致
        if data is not None:
            for field in field_names:
                if field in fields:
                    merged_data[field].extend(data[field].tolist())
                else:
                    merged_data[field].extend([None] * len(data))

            max_length = max(max_length, len(data))

    # 填补较短列
    for field in field_names:
        if len(merged_data[field]) < max_length:
            merged_data[field].extend([None] * (max_length - len(merged_data[field])))

    # 创建DataFrame 去除空行 输出
    output_df = pd.DataFrame(merged_data)
    output_df.dropna(how='all', inplace=True)  # 删除空行
    output_df.to_csv('output.csv', index=False, encoding='utf-8-sig')
    print("😆Merged data has been written to output.csv.")


if __name__ == "__main__":
    merge_files_to_csv()
