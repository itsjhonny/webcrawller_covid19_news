import scrapy

from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest


def get_data(response):
    for item in response.xpath('//ol[@class="u-list-unstyled c-search"]').xpath('li'):
        try:

            try:
                descricao = item.css('p.c-headline__standfirst::text').get() + item.css(
                    'p.c-headline__standfirst').xpath('b/text()').get().split(None, 0)[0]

            except Exception as ex:

                descricao = item.css('p.c-headline__standfirst::text').get().split(None, 0)[0]

            yield {
                'fonte': 'https://www.folha.uol.com.br/',
                'titulo': item.css('h2.c-headline__title::text').get().split(None, 0)[0],
                'descricao': descricao,
                'dia': item.css('time.c-headline__dateline').xpath('@datetime').get().split('às')[0].replace('.',
                                                                                                             ' '),
                'link': item.css('div.c-headline__content').xpath('a/@href').get(),
                'noticia': None,
                'tags': None
            }

        except Exception:
            pass


class QuotesSpider(scrapy.Spider):
    name = "get_folhasp"
    start_urls = [
        'http://search.folha.uol.com.br/search?q=coronavirus&site=todos',
        # 'http://search.folha.uol.com.br/search?q=coronavirus&site=todos&sr=301'

    ]

    def __init__(self):
        self.databaseController = ApiRequest()
        self.limit_time = False
        self.name_crawl = 'LOG FOLHA SP: '

    def parse(self, response):
        if self.limit_time:
            return print(self.name_crawl + 'Finalizou busca dentro do periodo de 1 mes')
        try:

            try:
                nextPage = response.xpath(
                    '//ul[@class="c-pagination__list"]').css('li.c-pagination__arrow')[1].xpath('a/@href').get()
            except:
                nextPage = response.xpath(
                    '//ul[@class="c-pagination__list"]').css('li.c-pagination__arrow')[0].xpath('a/@href').get()

            for item in get_data(response):
                try:
                    data_request = {'link': item['link']}

                    if not self.databaseController.make_request('check_exist_database', data_request):
                        yield scrapy.Request(item['link'], meta={"item": item}, callback=self.extract_html)
                except:
                    pass

            print(nextPage)

            yield scrapy.Request(nextPage, callback=self.parse)
        except:
            print('finalizou')

    def extract_html(self, response):

        tools = CustonTools()
        tags = []
        item = response.meta["item"]

        formattedData = tools.format_data_folhasp(item['dia'])

        self.limit_time = tools.compare_dates(formattedData)

        item['dia'] = formattedData

        wordList = tools.get_key_word_list()

        try:
            html = response.xpath(
                '//div[@class="c-news__body"]').get()
        except:
            html = response.xpath(
                '//div[@class="c-news__content"]').get()

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

        if len(item['tags']) > 0:
            # print('vai limpar o html')
            try:
                html = tools.clean_html_class_folhasp(html)
                item['noticia'] = tools.cleanHTML(html)
                # return print(item['noticia'])
                # print('limpou noticia')
                print(self.name_crawl + 'NOVA ' + item['titulo'])
                # print(item['noticia'])
                # print('salvando')
                # print(item)
                if not self.databaseController.make_request('inserir', item):
                    print('Erro ao salvar no banco de dados')

                # print('chegou ao final do extract html')
            except Exception as ex:

                # print('erro na noticia: ' + item['link'])
                # print(ex)
                pass

        else:
            print(self.name_crawl + 'Noticia não possui tags ' + item['link'])

        yield item
