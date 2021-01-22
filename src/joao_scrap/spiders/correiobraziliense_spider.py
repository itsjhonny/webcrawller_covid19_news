import requests
import scrapy

from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest


def get_data(response):
    for item in response:
        if 'Resumo do dia' not in item['title']:
            yield {
                'fonte': 'https://www.correiobraziliense.com.br',
                'titulo': item['title'],
                'descricao': item['description'],
                'dia': item['date_time'].split()[2],
                'link': item['url'],
                'noticia': None,
                'tags': None
            }


class QuotesSpider(scrapy.Spider):
    name = "get_correiobraziliense"
    start_urls = [
        'https://www.correiobraziliense.com.br/busca/coronavirus?json=63c055b-c8a7-4010-92c6-01803d6e752e&offset=0',

    ]

    def __init__(self):
        self.databaseController = ApiRequest()
        self.limit_time = False

    def parse(self, response):
        if self.limit_time:
            return print('Finalizou busca dentro do periodo de 1 mes')
        request = None
        try:
            request = requests.get(url=response.url)
        except requests.exceptions.RequestException as e:
            print(e)
            pass

        # extracting data in json format
        data = request.json()
        try:
            nextPage = data['next']

            for item in get_data(data['news']):
                data_request = {'link': item['link']}
                if not self.databaseController.make_request('check_exist_database', data_request):
                    print('NOVA ' + item['titulo'])
                    yield scrapy.Request(item['link'], meta={"item": item}, callback=self.extract_html)

            print(nextPage)
            yield scrapy.Request(nextPage, callback=self.parse)

        except:
            print('finalizou')

    def extract_html(self, response):
        tools = CustonTools()
        tags = []
        item = response.meta["item"]
        formatted_data = tools.format_dia(item['dia'])
        self.limit_time = tools.compare_dates(formatted_data)

        item['dia'] = formatted_data
        word_list = tools.get_key_word_list()
        try:
            html = response.xpath(
                '//div[@class="txt-serif js-article-box article-box article-box-capitalize mt-15"]').get()
        except:
            print('falhou ao obter html' + item['link'])

        for word in word_list:

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
                # print('vai salvar no banco')
                if not self.databaseController.make_request('inserir', item):
                    print('Erro ao salvar no banco de dados')
                # print('chegou ao final do extract html')
            except Exception as ex:
                print('erro na noticia: ' + item['link'])
                print(ex)
                pass
        else:
            # print('Noticia não possui tags ' + item['link'])
            pass
        return item
