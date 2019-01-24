import requests
from bs4 import BeautifulSoup as bs
import re
import wget
from lxml.html.clean import Cleaner

def link():
    '''Генерируем ссылки для пагинации'''
    url = []
    for i in range(1,421):
        url.append("http://www.mkyzyl.ru/?PAGEN_1=%s" %i)
    return url

def sanitize(dirty_html):
    '''функция очистки мусора html'''
    cleaner = Cleaner(page_structure=True,
                  meta=True,
                  embedded=True,
                  links=True,
                  style=True,
                  processing_instructions=True,
                  inline_style=True,
                  scripts=True,
                  javascript=True,
                  comments=True,
                  frames=True,
                  forms=True,
                  annoying_tags=True,
                  remove_unknown_tags=True,
                  safe_attrs_only=True,
                  safe_attrs=frozenset(['src','color', 'href', 'title', 'class', 'name', 'id']),
                  remove_tags=('span', 'font', 'div', 'br')
                  )
    return cleaner.clean_html(dirty_html)

def parser_page(url):
    '''Функция парсинга и сохранения данных'''
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    response = requests.get(url, headers=headers ).text
    soup = bs(response, 'html.parser')
    tag = (soup.findAll('p', attrs={'class': 'news-item'}))

    with open( 'news.txt', 'a', encoding='utf8') as file:
        for i in tag:
            url_full = "http://www.mkyzyl.ru" + (i.find("a").get('href'))
            response_page = requests.get(url_full, headers=headers).text
            soup_page = bs(response_page, 'html.parser')
            title = (soup_page.find("div", {"class": "welcome"})).text.strip()
            content_page = str((soup_page.findAll("div", {"class": "news"})[1:])[0].findAll("p")[1])
            content = (sanitize(content_page))
            image_page = (soup_page.findAll("div", {"class": "news"})[1:])[0].findAll("img")

            if not title and not content:
                print ("not ok")
            else:
                if not image_page:
                    image = ''
                    download = ''
                else:
                    for img in image_page:
                        image = ("http://www.mkyzyl.ru" + img['src'])
                        try:
                            download = (wget.download(image, out="d:/mykyzyl/image" ))
                        except:
                            download = ''
                news = {'title':title, 'content': content, 'image': image, 'download_img':download}
                print (news)
                file.write(str(news))
    file.close()

for i in link():
    parser_page(i)
