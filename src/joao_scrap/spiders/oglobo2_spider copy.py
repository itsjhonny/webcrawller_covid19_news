import urllib.parse as urlparse

import requests
import scrapy

from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest


def get_data(response):
    for item in response:
        yield {
            'fonte': 'https://oglobo.globo.com/',
            'titulo': item['titulo'],
            'descricao': None,
            'dia': None,
            'link': item['url'],
            'noticia': None,
            'tags': None
        }


class QuotesSpider(scrapy.Spider):
    name = "get_oglobo2"
    start_urls = [
        'https://scrapy.org',

    ]

    def __init__(self, **kwargs):
        self.limit_time = False
        self.name_crawl = 'LOG OGLOBO:'
        self.databaseController = ApiRequest()
        self.link = 'https://oglobo.globo.com/api/v1/vermais/24219742/conteudo.json?pagina=0&versao=v1' \
                    '&tiposDeConteudo=materia,coluna,infografico,listaFatos,materiaEmCapitulos,linkExterno '

    def parse(self, response):

        is_enabled = True

        while is_enabled and not self.limit_time:

            r = requests.get(self.link)

            # extracting data in json format
            data = r.json()[0]

            if len(data['conteudos']) > 0:
                parsed = urlparse.urlparse(data['paginacao']['urlProxima'])
                self.link = 'https://oglobo.globo.com/api/v1/vermais/24219742/conteudo.json?' + parsed.query
                for item in get_data(data['conteudos']):

                    data_request = {'link': item['link']}

                    if not self.databaseController.make_request('check_exist_database', data_request):

                        yield scrapy.Request(item['link'], meta={"item": item}, callback=self.extract_html)

                print(self.name_crawl + 'nextPage ' + self.link)

            else:
                is_enabled = False

        print(self.name_crawl + 'Finalizou busca dentro do periodo de 1 mes')

    def extract_html(self, response):
        tools = CustonTools()
        tags = []
        item = response.meta["item"]

        dia = response.xpath('//div[@class="article__date"]/text()').get().split(' ')[0].replace(' ', '').replace('\n',
                                                                                                                  ' ').replace(
            '\r', '')
        item['descricao'] = response.xpath('//div[@class="article__subtitle"]/text()').get().replace('\n', ' ').replace(
            '\r', '')

        formattedData = tools.format_dia(dia)
        self.limit_time = tools.compare_dates(formattedData)
        item['dia'] = formattedData

        wordList = tools.get_key_word_list()

        html = response.xpath(
            '//div[@class="article__content-container protected-content"]').get()
        if not html:
            print('pegou main')
            html = response.css('main').get()

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
                html = tools.clean_html_class_oglobo(html)
                item['noticia'] = tools.cleanHTML(html)

                print(self.name_crawl + 'NOVA ' + item['titulo'])
                if not self.databaseController.make_request('inserir', item):
                    print(self.name_crawl + 'Erro ao salvar no banco de dados')
                # print('armazenou noticia ' + item['titulo'])
                # print('chegou ao final do extract html')
            except Exception as ex:
                print('erro na noticia: ' + item['link'])
                print(ex)
                pass

        else:
            # print(self.name_crawl + 'Noticia não possui tags ' + item['link'])
            pass

        yield item
