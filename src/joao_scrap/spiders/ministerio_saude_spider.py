import scrapy

from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest


def get_data(response):
    for quote in response.css('div.tileItem'):
        yield {
            'fonte': 'https://www.saude.gov.br',
            'titulo': quote.css('h2.tileHeadline').css('a::text').get(),
            'descricao': quote.css('div.tileItem').css('span.description').xpath('p/text()').get(),
            'dia': quote.xpath('div')[1].xpath('ul/li/text()')[1].get(),
            'link': 'https://www.saude.gov.br' + quote.css('h2.tileHeadline').xpath('a/@href').get(),
            'noticias': None,
            'tags': None
        }


class QuotesSpider(scrapy.Spider):
    name = "get_ministerio_saude"
    start_urls = [
        'https://www.saude.gov.br/noticias?filter-search=coronavirus&limit=0',
    ]

    def __init__(self):
        self.limit_time = False
        self.name_crawl = 'Ministerio da Saude: '

    def parse(self, response):

        noticias = get_data(response)
        for item in noticias:
            yield scrapy.Request(item['link'], meta={"item": item}, callback=self.parse_page)

    def parse_page(self, response):

        databaseController = ApiRequest()
        item = response.meta["item"]

        data_request = {'link': item['link']}
        is_inDatabase = databaseController.make_request('check_exist_database', data_request)
        if is_inDatabase:
            return

        tools = CustonTools()
        wordList = tools.get_key_word_list()
        tags = []
        formattedData = tools.format_dia(item['dia'])
        item['dia'] = formattedData

        self.limit_time = tools.compare_dates(formattedData)

        if self.limit_time:
            return print(self.name_crawl + 'Finalizou busca dentro do periodo de 1 mes')

        html = response.css('div.item-page').get()
        for word in wordList:

            isWordInHtml = tools.check_word_in_html(word)(html)

            if isWordInHtml is None:
                pass
            else:
                tags.append(word)
                item['noticia'] = tools.cleanHTML(html)
                item['tags'] = ','.join(str(tag) for tag in tags)

        print(self.name_crawl + 'NOVA ' + item['titulo'])
        if not databaseController.make_request('inserir', item):
            print(self.name_crawl + 'Erro ao salvar no banco de dados')
