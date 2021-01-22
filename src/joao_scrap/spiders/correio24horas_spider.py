import scrapy

from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest


def get_data(response):
    for item in response.css('li.noticia-resultado-busca-responsivo__news__item'):
        yield {
            'fonte': 'https://www.correio24horas.com.br',
            'titulo': item.css('div.noticia-resultado-busca-responsivo__news__item__title').xpath('span/text()').get(),
            'descricao': item.css('div.noticia-resultado-busca-responsivo__news__item__description').xpath(
                'span/text()').get(),
            'dia': item.css('time.noticia-resultado-busca-responsivo__news__item__date::text').get().split()[0],
            'link': item.xpath('a/@href').get(),
            'noticia': None,
            'tags': None
        }


class QuotesSpider(scrapy.Spider):
    name = "get_correio24horas"
    start_urls = [
        'https://www.correio24horas.com.br/resultado-de-pesquisa/pagina/1/busca/coronavirus/',

    ]

    def __init__(self):

        self.databaseController = ApiRequest()
        self.limit_time = False
        self.name_crawl = 'LOG CORREIO 24 HORAS:'

    def parse(self, response):

        if self.limit_time:
            return print(self.name_crawl + 'Finalizou busca dentro do periodo de 1 mes')

        nextPage = response.xpath(
            '//div[@class="pagination-responsivo--next"]/a/@href').get()

        print(self.name_crawl + 'Nextpage: ' + nextPage)
        for item in get_data(response):
            data_request = {'link': item['link']}
            if not self.databaseController.make_request('check_exist_database', data_request):
                yield scrapy.Request(item['link'], meta={"item": item}, callback=self.extract_html)

        yield scrapy.Request(nextPage, callback=self.parse)

    def extract_html(self, response):
        tools = CustonTools()
        tags = []
        item = response.meta["item"]

        formatted_date = tools.format_dia(item['dia'])
        item['dia'] = formatted_date
        self.limit_time = tools.compare_dates(formatted_date)

        wordList = tools.get_key_word_list()
        item['descricao'] = response.xpath(
            '//div[@class="noticias-single__description visible-lg"]/text()').get()

        html = response.xpath(
            '//div[@class="noticias-single__content"]').get()

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
                # print('erro na noticia: ' + item['link'])
                # print(err)
                pass
        else:
            # print('Noticia não possui tags ' + item['link'])
            pass

        yield item
