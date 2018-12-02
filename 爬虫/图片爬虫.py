import requests
from bs4 import BeautifulSoup

def get_photo(url,arrts,name='img'):
    r = requests.get(url)
    print(r.status_code)
    html = r.content
    soup = BeautifulSoup(html,'html.parser')
    number = 0

    for pic in soup.find_all(name,arrts):
        p = pic.get('src')  
        x = p[-10:]  #截取字符串作为图片名
        number += 1
        print('正在下载'+str(number) + '张...')  
    
        #下载到本地
        url = requests.get(p)
        path_name = r'D:\图片！图片\python爬虫图片\\' + str(x)  #文件路径和文件名
        with open(path_name,'wb') as file:  
            file.write(url.content)

url = ('https://user.qzone.qq.com/1327764620/infocenter')
arrts = _class='j-pl-photoitem-img'
get_photo(url,arrts)