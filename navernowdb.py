import requests
from bs4 import BeautifulSoup
import time
import datetime
from mysqlwith import connector


class naver_now:
    BASE_URI = 'https://entertain.naver.com'
    PAGE_URI = BASE_URI + (
        '/now'
        '?sid=%(sid)s'
        '&date=%(date)s'
        '&page=%(page)s'
    )


    def __init__(self):
        self.sid = '7a5'
        self.date = datetime.date.today()
        self.page = 1
        self.max = 100
        self.contents = []
        self.mysql_config = {
            'db': 'apps',
            'host': 'localhost',
            'user': 'rusk',
            'passwd': 'alsueopseo'
        }


    def fetch_posts(self):
        self.fetch_from_db()
        self.fetch_timeline()
        self.fetch_texts()


    def fetch_from_db(self):
        with connector(self.mysql_config) as connect:
            cursor = connect.cursor()
            cursor.execute('select uri from navernow order by id desc limit 1')
            self.latest_uri = cursor.fetchone()[0]
            cursor.close()


    def write_to_db(self):
        with connector(self.mysql_config) as connect:
            cursor = connect.cursor()
            for item in reversed(self.contents):
                title = item['title'].replace('\'', u'\\\'')
                text = item['text'].replace('\'', u'\\\'')
                cursor.execute("insert into navernow (uri, title, time, text, thumbnail) values ('%s', '%s', '%s', '%s', '%s')"
                                % (item['uri'], title, item['time'], text, item['thumbnail']))
            cursor.close()


    def fetch_timeline(self):
        uri = self.PAGE_URI % {
            'sid': self.sid,
            'date': self.date,
            'page': self.page
        }
        res = requests.get(uri)
        soup = BeautifulSoup(res.text, 'html.parser')
        lst = soup.select_one('.news_lst')
        soup = BeautifulSoup(str(lst), 'html.parser')
        items = soup.select('li')
        if items[0].string == '기사가 없습니다.':
            return
        for item in items:
            content = {
                'title': item.select_one('.tit').get_text(),
                'uri': item.select_one('.tit')['href'],
                'ago': item.select_one('em').get_text()
                }
            if content['uri'] == self.latest_uri:
                print('Listed %s Posts' % len(self.contents))
                return
            try:
                content['thumbnail'] = item.select_one('img')['src']
            except TypeError:
                content['thumbnail'] = 'NULL'
            self.contents.append(content)
        print('Listed %s Posts' % len(self.contents))
        if len(self.contents) >= self.max:
            return
        time.sleep(0.1)
        self.page += 1
        self.fetch_timeline()


    def fetch_texts(self):
        count = 0
        for item in self.contents:
            count += 1
            uri = self.BASE_URI + item['uri']
            res = requests.get(uri)
            soup = BeautifulSoup(res.text, 'html.parser')
            item['time'] = soup.select_one('.article_info em').get_text()
            text = soup.select_one('#articeBody').get_text()
            text = text.replace('\n', '')
            item['text'] = text.replace('\t', '')
            print('Fetched %s %s / %s' % (uri, count, len(self.contents)))
            time.sleep(0.1)


def main():
    contents = naver_now()
    contents.fetch_posts()
    contents.write_to_db()
    print('Done')


if __name__ == '__main__':
    main()

