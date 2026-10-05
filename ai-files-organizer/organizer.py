import os
import json
from openai import OpenAI
import shutil

client = OpenAI(
    api_key="",
    base_url="https://api.deepseek.com"
)

def get_files(folder):
    """拿到文件夹里的所有文件（不包含子文件）"""
    files = []
    for name in os.listdir(folder):
        path = os.path.join(folder,name)
        if os.path.isfile(path):
            files.append(name)
    return files


def classify(files):
    """把一批文件名交给AI,返回{文件名:类别}的字典"""
    file_list = "\n".join(files)
    prompt = f"""你是一个文件整理助手。请根据下面的文件名，判断每个文件属于哪个类别。类别只能是：图片、文档、视频、音频、代码、压缩包、其他。严格按照以下josn格式输出,不要输出其他内容:
{{文件名1:类别,文件名2:类别}}
文件名列表:
{file_list}    
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages = [{"role":"user","content":prompt}]
    )
    text = response.choices[0].message.content
    text = text.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("JSON解析失败,原始文本:",text)
        raise

def organize(folder,mapping):
    """按照判断结果把文件移动进对应子文件夹"""
    for filename,category in mapping.items():
        src = os.path.join(folder,filename)

        if not os.path.exists(src):
            continue
        dst_dir = os.path.join(folder,category)
        os.makedirs(dst_dir,exist_ok=True)

        shutil.move(src,os.path.join(dst_dir,filename))
        print(f"{filename}->{category}/")

#测试入口
if __name__ == "__main__":
    folder = r"D:\Python3910\案例\例"

    files = get_files(folder)
    print(f"发现{len(files)}个文件")

    mapping = classify(files)
    organize(folder,mapping)

    print("整理完成！")

