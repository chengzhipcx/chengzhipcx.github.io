from markdown import markdown
import os
from datetime import datetime
import argparse

def replace_multiple(html_file, replacements,target_file):
    with open(html_file, 'r',encoding='utf-8') as file:
        html_content = file.read()

        # 逐一替换标识符为指定内容
        for identifier, replacement in replacements.items():
            html_content = html_content.replace(identifier, replacement)
            
        # 将新内容写回文件中
        with open(targetfile, 'w',encoding='utf-8') as new_file:
            new_file.write(html_content)
        print("内容替换成功！")

# 获取当前文件所在的目录路径
current_path = os.path.dirname(__file__)

# 获取当前目录的上级目录路径
parent_path = os.path.dirname(current_path)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('-m',help='md name')
    args=parser.parse_args()
    mdfilename=args.m
    file = open(os.path.join(parent_path,'md', mdfilename),'r',encoding='utf-8').read()

    html = markdown(file)
    # print(html)
    target_name=mdfilename.split('.')[0]

    tempfile = os.path.join(current_path,'temp.html')
    targetfile = os.path.join(parent_path,'site',target_name+'.html')

    replacements = {
        '{{content}}': html,
        '{{title}}': target_name,
        '{{date}}': str(datetime.now().date())
    }
    replace_multiple(tempfile, replacements,targetfile)
    # with open('ret.html', 'w', encoding='utf-8') as file:
    #     file.write(html)



