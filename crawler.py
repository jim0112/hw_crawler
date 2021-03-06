from bs4 import BeautifulSoup
import requests
from lxml import etree
from datetime import datetime
from time import *



class Crawler(object):
    def __init__(self,
                 base_url='https://www.csie.ntu.edu.tw/news/',
                 rel_url='news.php?class=101'):
        self.base_url = base_url
        self.rel_url = rel_url

    def crawl(self, start_date, end_date,
              date_thres=datetime(2012, 1, 1)):
        """Main crawl API

        1. Note that you need to sleep 0.1 seconds for any request.
        2. It is welcome to modify TA's template.
        """
        if end_date < date_thres:
            end_date = date_thres
        contents = list()
        page_num = 0
        while True:
            rets, last_date = self.crawl_page(
                start_date, end_date, page=f'&no={page_num}')
            page_num += 10
            if rets:
                contents += rets
            if last_date < start_date:
                break
                
        return contents

    def crawl_page(self, start_date, end_date, page=''):
        """Parse ten rows of the given page

        Parameters:
            start_date (datetime): the start date (included)
            end_date (datetime): the end date (included)
            page (str): the relative url specified page num

        Returns:
            content (list): a list of date, title, and content
            last_date (datetime): the smallest date in the page
        """
        res = requests.get(
            self.base_url + self.rel_url + page,
            headers={'Accept-Language':
                     'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6'}
        ).content.decode()
        sleep(0.1)
        # TODO: parse the response and get dates, titles and relative url with etree
        soup = BeautifulSoup(res, 'lxml')
        table = soup.find('table', {'id':'RSS_Table_page_news_1'})
        list_rows = table.tbody.find_all('tr')
        news_list = list()
        contents = list()
        for row in list_rows:
            news_list.append((row.td.text, row.find_all('td')[1].a.text, row.find_all('td')[1].a.attrs['href']))
        
        last_date = end_date
        for news in news_list:
            date_split = news[0].split('-')
            news_date = datetime(int(date_split[0]),int(date_split[1]),int(date_split[2]))
            news_url = self.base_url + news[2]
            news_content = self.crawl_content(news_url)
            if(last_date>news_date):
                last_date = news_date
            if(news_date>=start_date and news_date<=end_date):
                contents.append((news_date,news[1],news_content))
        #for rel_url in rel_urls:
            # TODO: 1. concatenate relative url to full url
            #       2. for each url call self.crawl_content
            #          to crawl the content
            #       3. append the date, title and content to
            #          contents


        return contents, last_date

    def crawl_content(self, url):
        """Crawl the content of given url

        For example, if the url is
        https://www.csie.ntu.edu.tw/news/news.php?Sn=15216
        then you are to crawl contents of
        ``Title : 我與DeepMind的A.I.研究之路, My A.I. Journey with DeepMind Date : 2019-12-27 2:20pm-3:30pm Location : R103, CSIE Speaker : 黃士傑博士, DeepMind Hosted by : Prof. Shou-De Lin Abstract: 我將與同學們分享，我博士班研究到加入DeepMind所參與的projects (AlphaGo, AlphaStar與AlphaZero)，以及從我個人與DeepMind的視角對未來AI發展的展望。 Biography: 黃士傑, Aja Huang 台灣人，國立臺灣師範大學資訊工程研究所博士，現為DeepMind Staff Research Scientist。``
        """
        doc = requests.get(url).content.decode()
        sleep(0.1)
        soup = BeautifulSoup(doc, 'lxml')
        return soup.find('div',{'class':'editor content'}).text


#for testing
#crawler = Crawler()
#content = crawler.crawl(datetime(2019,12,1), datetime(2019,12,20))

