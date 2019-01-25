# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as bs
import re
import bleach
import os
import pymysql.cursors

def link():
    url = []
    for i in range(1,421):
        url.append("http://www.mkyzyl.ru/?PAGEN_1=%s" %i)
    return url

def html_clener(html):
    clear = bleach.clean(html,
                         tags=['strong', 'p', 'img', 'br'],
                         attributes={'a': ['href'], 'img': ['alt', 'src']},
                         strip=False )
    clear = re.sub("'", '', clear)
    return clear

def parser_page(url):
    connection = pymysql.connect( host='localhost',
                                  user='***',
                                  password='***',
                                  db='***',
                                  charset='utf8mb4',
                                  init_command='SET NAMES UTF8',
                                  cursorclass=pymysql.cursors.DictCursor )

    proxies = {"http": "http://***:***/"} #прокси, на тот случай, если запушен денвер и сайт
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    response = requests.get(url, headers=headers, proxies=proxies).text
    soup = bs(response, 'html.parser')
    tag = (soup.findAll('p', attrs={'class': 'news-item'}))
    time = (soup.findAll('span', attrs={'class': 'news-date-time'}))
    cnt = []
    num = len(cnt)
    for i in tag:
        url_full = "http://www.mkyzyl.ru" + (i.find("a").get('href'))
        response_page = requests.get(url_full, headers=headers, proxies=proxies).text
        soup_page = bs(response_page, 'html.parser')
        title = (soup_page.find( "div", {"class": "welcome"} )).text.strip()
        title = title[0:170]

        cnt.append(title)
        content_page = str((soup_page.findAll("div", {"class": "news"})[1:])[0].findAll("p")[1])
        content = html_clener(content_page)

        date =  str(time[0].text)
        date = date.split('.')
        date = (date[2] + "-" + date[1] + "-" + date[0] + " 00:00:00")

        image_page = (soup_page.findAll("div", {"class": "news"} )[1:])[0].findAll("img")
        if not image_page:
            image = ''
        else:
            for img in image_page:
                image = 'wp-content/uploads/old/' + os.path.basename(img['src'])
        if not title and not content and not date:
            print("not ok")
        else:
            sql = u"""
        INSERT INTO `kzl` (`ID`, `post_author`, `post_date`, `post_date_gmt`, `post_content`, `post_title`, `post_excerpt`, `post_status`, `comment_status`, `ping_status`, `post_password`, `post_name`, `to_ping`, `pinged`, `post_modified`, `post_modified_gmt`, `post_content_filtered`, `post_parent`, `guid`, `menu_order`, `post_type`, `post_mime_type`, `comment_count`) VALUES
        ("""+str(num)+""", 1, '"""+date+"""', '"""+date+"""', '<img class="alignleft size-medium" src="/"""+image+""""  />"""+content+"""', '"""+title+"""', '', 'publish', 'open', 'open', '', '"""+title+"""', '', '', '"""+date+"""', '"""+date+"""', '', 0, 'http://www.mkyzyl.ru/?p="""+str(num)+"""', 0, 'post', '', 0);
            """
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    connection.commit()
                    print (title)
            except Exception as e: print( e )
for i in link():
    parser_page(i)
