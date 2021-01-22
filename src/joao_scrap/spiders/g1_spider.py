import datetime
import calendar

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest
from joao_scrap.tools.cleanHTML import data_inicial, data_final

def get_data(response):
    for li in response:
        if li.get_attribute('class') == 'widget widget--card widget--info':
            yield {

                'fonte': 'https://g1.globo.com/',
                'titulo': li.find_element_by_class_name('widget--info__text-container').find_element_by_tag_name(
                    'a').find_element_by_tag_name('div').text,
                'descricao': li.find_element_by_class_name('widget--info__description').text,
                'dia': li.find_element_by_class_name('widget--info__meta').get_attribute('textContent'),
                'link': li.find_element_by_class_name('widget--info__text-container').find_element_by_tag_name(
                    'a').get_attribute('href'),
                'noticia': None,
                'tags': None
            }


class QuotesSpider(scrapy.Spider):
    name = 'get_g1'
    start_urls = [
        'https://scrapy.org',

    ]

    def __init__(self):
        self.databaseController = ApiRequest()
        self.arrayNoticias = []
        self.indexData = 0
        self.name_crawl = 'LOG G1: '
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors')
        #self.driver = webdriver.Chrome(
            #ChromeDriverManager().install(), options=chrome_options)
        #self.driver2 = webdriver.Chrome(
            #ChromeDriverManager().install(), options=chrome_options)

        self.driver =  webdriver.Remote("http://localhost:4444/wd/hub", options=chrome_options)
        self.driver2 =  webdriver.Remote("http://localhost:4444/wd/hub", options=chrome_options)

        

        self.dates = [
            # {'dataInicial': str(ano) + '-01-01', 'dataFinal':str(ano) + '-01-31'},
            # {'dataInicial': str(ano) + '-02-01', 'dataFinal':str(ano) + '-02-29'},
            # {'dataInicial': str(ano) + '-03-01', 'dataFinal':str(ano) + '-03-31'},
            # {'dataInicial': str(ano) + '-04-01', 'dataFinal':str(ano) + '-04-30'},
            # {'dataInicial': str(ano) + '-05-01', 'dataFinal':str(ano) + '-05-31'},
            # {'dataInicial':  str(ano) + '-06-01', 'dataFinal': str(ano) + '-06-30'},
            # {'dataInicial': str(ano) + '-07-01',
            # 'dataFinal': str(ano) + '-07-31'},
            # {'dataInicial': str(ano) + '-08-01',
            # 'dataFinal': str(ano) + '-08-31'} 
            #  {'dataInicial': str(ano) + '-09-01',
            # 'dataFinal': str(ano) + '-09-30'},
            #  {'dataInicial': str(ano) + '-10-29',
            #'dataFinal': str(ano) + '-10-31'}
            # {'dataInicial': '2020-12-17',
            # 'dataFinal': str(ano) + '-01-04'}
            {'dataInicial': str(data_inicial), 'dataFinal': str(data_final)}

        ]
        start_at = 0

        print(self.name_crawl + 'DATA ' +
              self.dates[start_at]['dataInicial'] + ' ' + self.dates[start_at]['dataFinal'])
        self.parse('https://g1.globo.com/busca/?q=coronavirus&page=1', start_at)

    def parse(self, link, dataIndex):

        data = '&order=recent&species=notícias&from={}T00%3A00%3A00-0300&to={}T23%3A59%3A59-0300'.format(
            self.dates[dataIndex]['dataInicial'], self.dates[dataIndex]['dataFinal'])



        #print('Link a pesquisar ' + link+data)
        self.driver.get(link + data)

        try:
            nextPage = self.driver.find_element_by_xpath(
                "//a[@class='fundo-cor-produto pagination__load-more']").get_attribute('href')
            # print('pegou link proxima pagina')

            response = self.driver.find_element_by_class_name(
                "results__list").find_elements_by_tag_name("li")

            for item in get_data(response):
                data_request = {'titulo': item['titulo']}
                if not self.databaseController.make_request('check_exist_database', data_request):
                    # print('\n|-- NOVA ' + item['titulo'])
                    self.extract_html(item)
                else:
                    # print('noticia já existe ')
                    pass

                    # print('\n\n PROXIMA PAGINA')
            print(self.name_crawl + 'next page ' + nextPage)
            self.parse(nextPage, dataIndex)

        except Exception as ex:
            print(ex)
            if dataIndex + 1 < len(self.dates):
                # print('proxima data ')
                print('\n\nDATA ' + self.dates[dataIndex]['dataInicial'] +
                      ' ' + self.dates[dataIndex]['dataFinal'])
                self.parse(
                    'https://g1.globo.com/busca/?q=coronavirus&page=1', dataIndex + 1)

            else:
                print(self.name_crawl + 'finalizou ')
                
                #self.parse(
                #    'https://g1.globo.com/busca/?q=coronavirus&page=1', 0)

    def extract_html(self, item):
        tools = CustonTools()
        self.driver2.get(item['link'])
        # print(item['link'])
        try:
            time = self.driver2.find_element_by_tag_name('time').text
            item['dia'] = tools.format_dia(time.split(' ')[0])
            self.limit_time = tools.compare_dates(item['dia'])

            if self.limit_time:
                print(self.name_crawl + 'Noticia passou da data limite: ' + item['link'])
                return



        except Exception as ex:
            item['dia'] = 'error_time'
            print(ex)
            pass

        wordList = tools.get_key_word_list()
        tags = []
        # print(item['dia'])

        try:
            html = self.driver2.find_element_by_tag_name(
            'article').get_attribute('innerHTML')
        except Exception as ex:
            print(ex)
            return

        # print('pegou html')
        

        for word in wordList:

            isWordInHtml = tools.check_word_in_html(word)(html)

            if isWordInHtml is None:
                pass
            else:

                tags.append(word)
                # print('contem tag')
                item['tags'] = ','.join(str(tag) for tag in tags)
                # print('tags adicionadas ' + word)

        if not item['tags'] is None:
            # print('vai limpar o html')
            try:
                item['noticia'] = tools.cleanHTML(html)
                # print(item)
                # print('limpou noticia')
                # print('vai salvar no banco')
                print(self.name_crawl + 'NOVA ' + item['titulo'])

                if not self.databaseController.make_request('inserir', item):
                    print(self.name_crawl + 'Erro ao salvar no banco de dados')

                # print('chegou ao final do extract html')
            except:
                print(self.name_crawl + 'erro na noticia: ' + item['link'])
                pass
        else:
            print(self.name_crawl + 'Noticia não possui tags ' + item['link'])

        return item
