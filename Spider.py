# -*-coding:utf-8 -*-
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


# 获取豆瓣电影的题目和链接，并转存到csv文件中
def GetMovieInfo():
    url_titlelist = []
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    for i in range(0, 251, 25):
        re = requests.get('https://movie.douban.com/top250?start=' + str(i) + '&filter=', headers=header)
        soup = BeautifulSoup(re.text, 'lxml')
        urls = soup.findAll(class_='hd')
        # url.a['href'] 获取链接  url.span.text 获取电影名称
        for url in urls:
            url_titlelist.append({'movietitle': url.span.text, 'movieurl': url.a['href']})
    # 创建Dataframe格式数据,通过字典格式进行转入
    df = pd.DataFrame(url_titlelist)
    df.to_csv('data/douban_movie_url.csv')


def GetDetailInfo():
    # 获取电影的详细信息，包括导演、编剧、主演、类型、制作地区、语言、上映时间、片长、评分、评价人数、观看人数、想看人数、短评条数
    data = []
    movie = pd.read_csv('data/douban_movie_url.csv')
    print(movie)
    MovieDetail = []
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'Cookie': 'bid=IWe9Z6busEk; douban-fav-remind=1; gr_user_id=f7fae037-6b68-4d42-8a9e-19a1ef3263a7; _vwo_uuid_v2=DB1D5D334A6BE3FD5143EAF4C7FD52463|f63a15d9f0accbd1c8836fedba0591ff; viewed="10571608_10571602_26589104_1195595"; __yadk_uid=Ife4NimEiP6V0taky1FCMpfTWLdNfRan; ll="118136"; trc_cookie_storage=taboola%2520global%253Auser-id%3De88de203-688b-415e-9d09-0e40d41140ec-tuct41d9fc9; __utmv=30149280.17939; douban-profile-remind=1; __gads=ID=6d22200e8d8100ab:T=1580716605:S=ALNI_MY8d2gzAYOhbwuwAKgaSbx9kRa8kw; __utmc=30149280; __utmz=30149280.1582461492.18.13.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmc=223695111; __utmz=223695111.1582461492.11.6.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ct=y; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1582518519%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Dw3K7KtSpdRTRt9Nso7KvfEqEScg3YYFJZms1zZ0A_jhdFN1ZhldskLw7VdKnHSb7%26wd%3D%26eqid%3De6fdfb68004b8856000000035e527231%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.1262479007.1562647114.1582513563.1582518519.22; __utmb=30149280.0.10.1582518519; __utma=223695111.770823807.1572251330.1582513563.1582518519.15; __utmb=223695111.0.10.1582518519; ap_v=0,6.0; dbcl2="179397940:9GTKde9XxvY"; ck=6E9C; push_doumail_num=0; push_noty_num=0; _pk_id.100001.4cf6=ba941b513938cd23.1572251329.15.1582519262.1582514328.'
        }
    for url in movie['movieurl'].values.tolist():
        re = requests.get(url, headers=header)
        time.sleep(1)
        soup = BeautifulSoup(re.text, 'lxml')
        try:
            title = soup.find('h1').span.text  # 标题
            director = soup.find(class_='attrs').a.text  # 导演
            Screenwriter = soup.findAll(class_='attrs')[1].text  # 编剧
            main_performer = soup.findAll(class_='attrs')[2].text.split('/')  # 这里只选择前3主演
            main_performer = main_performer[0] + '/' + main_performer[1] + '/' + main_performer[2]
            Type = soup.findAll(class_='pl')[3].find_next_siblings("span")
            Types = ''
            for type in Type:
                if (type.text == '制片国家/地区:' or type.text == '官方网站:'):
                    break
                else:
                    Types += type.text + '/'
            Types = Types[:-1]  # 类型

            region = soup.findAll(class_='pl')[4]
            if (region.text == '官方网站:'):
                region = soup.findAll(class_='pl')[5]
            region = region.next.next  # 制作地区

            Language = soup.findAll(class_='pl')[5]
            if (Language.text == '制片国家/地区'):
                Language = soup.findAll(class_='pl')[6]
            Language = Language.next.next  # 语言

            ShowtTime = soup.findAll(class_='pl')[6]
            if (ShowtTime.text == '语言:'):
                ShowtTime = soup.findAll(class_='pl')[7]
            ShowtTime = ShowtTime.find_next_sibling("span").text.split('(')[0]  # 上映日期

            Film_length = soup.findAll(class_='pl')[7]
            if (Film_length.text == '上映日期:'):
                Film_length = soup.findAll(class_='pl')[8]
            Film_length = Film_length.find_next_sibling("span").text[:-2]  # 片长

            score = soup.find('strong', class_='ll rating_num').text  # 评分
            rating_people = soup.find('a', class_='rating_people').text.strip()[:-3]  # 评价人数
            watching_people = soup.find('div', 'subject-others-interests-ft').a.text[:-3]  # 看过人数
            wtsee_people = soup.find('div', 'subject-others-interests-ft').a.find_next_siblings("a")[0].text[
                           :-3]  # 想看人数
            comments_people = soup.find('div', class_='mod-hd').h2.span.a.text.split(' ')[1]  # 短评人数
            # 到这里 前面数据已经测试完毕 接下来就是写入文件
            AllInfo = {'Title': title, 'Director': director, 'Screenwriter': Screenwriter,
                       'Main_performer': main_performer, 'Types': Types, 'Region': region, 'Language': Language,
                       'ShowTime': ShowtTime, 'Film_length': Film_length, 'Score': score,
                       'Rating_people': rating_people, 'Watching_people': watching_people, 'Wtsee_people': wtsee_people,
                       'Comments_people': comments_people}
            data.append(AllInfo)
            print(AllInfo)
        except:
            print('error')
            continue
    df = pd.DataFrame(data)
    df.to_csv('data/douban_movie_info.csv', index=False)  # 不把索引输入到文件中


# 导入数据，进行数据清洗，再将清洗后的数据进行不保存
def CleanData():
    movie_info = pd.read_csv('data/douban_movie_info.csv')
    movie_info['Title'] = [title[0] for title in movie_info['Title'].str.split(' ')]  # 只取中文标题
    # 提取出版年份
    movie_info['ShowtTime'] = pd.to_datetime(movie_info['ShowtTime'], errors='coerce').dt.year
    # 清洗片长数据
    movie_info['Film_length'] = [lenth[0] for lenth in movie_info['Film_length'].str.split('分')]
    flag = movie_info.to_csv('data/douban_movie_info2.0.csv', index=False)
    print(flag)

def run():
    # 获取豆瓣电影的题目和链接，并转存到csv文件中
    GetMovieInfo()
    # 获取电影的详细信息，包括导演、编剧、主演、类型、制作地区、语言、上映时间、片长、评分、评价人数、观看人数、想看人数、短评条数
    GetDetailInfo()
    # 数据清洗
    CleanData()



if __name__ == '__main__':
    run()