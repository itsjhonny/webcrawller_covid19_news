import json

import scrapy

from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest


def get_data(response):
    for item in response.css('div.lista').xpath('section'):

        if item.css('div')[0].xpath('@class').extract() == "box":
            dia = item.css('div')[0].css('span.data-posts').xpath('text()').get().split('|')[0]
        else:
            dia = None

        yield {
            'fonte': 'https://www.estadao.com.br/',
            'titulo': item.css('div')[0].css('a.link-title').xpath('@title').get(),
            'descricao': item.css('div')[0].css('a.link-title').xpath('p/text()').get(),
            'dia': dia,
            'link': item.css('div')[0].css('a.link-title').xpath('@href').get(),
            'noticia': None,
            'tags': None
        }


class QuotesSpider(scrapy.Spider):
    name = "get_estadao"
    start_urls = [
        'https://busca.estadao.com.br/modulos/busca-resultado?modulo=busca-resultado&config[busca][page]=1&config['
        'busca][params]=tipo_conteudo%3DNot%25C3%25ADcias%26quando%3D%26q%3Dcoronavirus&ajax=1',

    ]

    def __init__(self):
        self.databaseController = ApiRequest()

        self.limit_time = False
        self.name_crawl = 'LOG ESTADAO: '

    def parse(self, response):
        if self.limit_time:
            return print(self.name_crawl + 'Finalizou busca dentro do periodo de 1 mes')
        try:

            nextPage = json.loads(response.xpath(
                '//a[@class="go more-list-news btn-mais fn brd-e"]/@data-config').get())['busca']['page']

            nextPage: int = int(nextPage) + 1
            linkNextPage = 'https://busca.estadao.com.br/modulos/busca-resultado?modulo=busca-resultado&config[' \
                           'busca][page]={0}&config[busca][' \
                           'params]=tipo_conteudo%3DNot%25C3%25ADcias%26quando%3D%26q%3Dcoronavirus&ajax=1'.format(
                nextPage)
            # print(nextPage)

            for item in get_data(response):
                data_request = {'link': item['link']}

                if not self.databaseController.make_request('check_exist_database', data_request):
                    # print(item['titulo'])
                    yield scrapy.Request(item['link'], meta={"item": item}, callback=self.extract_html)

            yield scrapy.Request(linkNextPage, callback=self.parse)
        except Exception as err:
            print(err)

    def extract_html(self, response):
        tools = CustonTools()
        tags = []
        item = response.meta["item"]

        if item['dia'] is None:
            dia = response.xpath(
                '//div[@class="n--noticia__state-desc"]/p/text()').get().split('|')[0][1:]

            item['dia'] = dia

        formattedData = tools.format_data_estadao(item['dia'])
        self.limit_time = tools.compare_dates(formattedData)

        item['dia'] = formattedData

        wordList = tools.get_key_word_list()

        html = response.xpath(
            '//div[@class="n--noticia__content content"]').get()

        for word in wordList:

            isWordInHtml = tools.check_word_in_html(word)(html)
            isWordInTitulo = tools.check_word_in_html(word)(item['titulo'])

            if isWordInHtml is None and isWordInTitulo is None:
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
                # print('limpou noticia')
                print(self.name_crawl + 'NOVA ' + item['titulo'])
                # print('vai salvar no banco')
                if not self.databaseController.make_request('inserir', item):
                    print(self.name_crawl + 'Erro ao salvar no banco de dados')

                # print('chegou ao final do extract html')
            except Exception as err:
                print('erro na noticia: ' + item['link'])
                print(err)
                pass
        else:
            print('Noticia não possui tags ' + item['link'])
        yield item
