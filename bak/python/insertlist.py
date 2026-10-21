from bs4 import BeautifulSoup
import os
from datetime import datetime
import random

# 获取当前文件所在的目录路径
current_path = os.path.dirname(__file__)

# 获取当前目录的上级目录路径
parent_path = os.path.dirname(current_path)

# 原始HTML文档
html_doc = open(os.path.join(parent_path,'site','index.html'),'r',encoding='utf-8').read()

# 解析HTML
soup = BeautifulSoup(html_doc, 'html.parser')

def insert_tag(title,dtail):
    date=str(datetime.now().date())
    image_num=random.randint(1, 11)
    # 创建要插入的新HTML内容
    new_html = '''
            <div class="art-model">
            <h3><a href="'''+title+'''.html" target="_blank">'''+title+'''</a></h3>
            <p class="dateview"> <span>发布时间：'''+date+'''</span> <span>作者：个人</span> <span>分类：网络</span> </p>
            <dl class="img-txt">
                <dt> <a href="'''+title+'''.html"><img src="images/'''+str(image_num)+'''.jpg" alt="'''+title+'''"
                    title="'''+title+'''"></a> </dt>
                <dd>
                <p class="deatil">　　'''+detial+'''</p>
                <a href="'''+title+'''.html" class="btn bg-f26868 c-fff" target="_blank">查看</a>
                </dd>
            </dl>
            </div>
    '''

    # 找到要插入的位置
    main_content_div =soup.find(class_="art-model")

    # 插入新内容
    main_content_div.insert_before(BeautifulSoup(new_html, 'html.parser'))

    # 输出修改后的HTML
    with open(os.path.join(parent_path,'site','index.html'),'w',encoding='utf-8') as file:
        file.write(soup.prettify())

title='爱你'
detial='我爱你啊'
insert_tag(title,detial)