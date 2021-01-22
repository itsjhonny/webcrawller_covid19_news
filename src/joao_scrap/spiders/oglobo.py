import scrapy
import urllib.parse
from scrapy.spiders import CrawlSpider, Rule
from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest
import time
class QuotesSpider(scrapy.Spider):
    name = "get_oglobo"
    start_urls = [
        'https://oglobo.globo.com/busca/?q=coronavirus',
    ]

    def parse(self, response):
        
        try:
            nextPage = response.xpath('//ul[@class="unstyled unbordered"]').css('li')[6].xpath('a/@href').get()

            for item in self.get_data(response):
                
                if self.check_exist_database(item['link']) == False: 
                    #print(item['titulo'])
                    yield scrapy.Request(item['link'], meta={"item": item}, callback=self.extract_html)

                      
            #print(nextPage)

            yield scrapy.Request('https://oglobo.globo.com/busca/' + nextPage, callback=self.parse)
        except:
            print('finalizou')


    def get_data(self, response):

        #  x = response.xpath('//ul[@class="resultado_da_busca unstyled"]').xpath('li')[0]
        #  data = x.css('p')[0].css('span::text')[1].get()
        #  link x.css('a.cor-produto').xpath('@href').get()
        #  title x.css('a.cor-produto').xpath('@title').get()
        #  descricao x.css('p')[1].xpath('string(.)').get()


        for item in response.xpath('//ul[@class="resultado_da_busca unstyled"]').xpath('li'): 
            link = item.css('a.cor-produto').xpath('@href').get()
            link_uncoded = urllib.parse.parse_qs(link[2:])['u'][0]

            yield {
                'fonte': 'https://oglobo.globo.com/',
                'titulo': str(item.css('a.cor-produto').xpath('@title').get()).replace('‘','').replace('’',''),
                'descricao': item.css('p')[1].xpath('string(.)').get(),
                'dia': item.css('p')[0].css('span::text')[1].get(),
                'link': link_uncoded,
                'noticia': None,
                'tags': None
            }

           


    def extract_html(self, response):
        tools = CustonTools()
        tags = []
        item = response.meta["item"]  
               
        formatedData = tools.format_data_oglobo(item['dia'])

        item['dia'] = formatedData
        

        wordList = tools.get_key_word_list()       

        html = response.xpath('//div[@class="article__content-container protected-content"]').get()
        if(not html):
            print('pegou main')
            html = response.css('main').get()
        

        for word in wordList:

            isWordInHtml = tools.check_word_in_html(word)(html)

            if isWordInHtml == None:
                pass
            else:
                
                tags.append(word)
                #print('contem tag')
                item['tags'] = ','.join(str(tag) for tag in tags)
                #print('tags adicionadas ' + word)
        
        if not item['tags'] == None:
            #print('vai limpar o html')
            try:
                html = tools.clean_html_class_oglobo(html)
                item['noticia'] = tools.cleanHTML(html)

                #self.save_to_database(item)  
                #print('armazenou noticia ' + item['titulo'])
                #print('chegou ao final do extract html')
            except:

                print('erro na noticia: ' + item['link'])
                pass     

            
 

        else:
            print('Noticia não possui tags ' + item['link'])


        yield item
        
    def check_exist_database(self,titulo):
        self.databaseController = ApiRequest()
        return self.databaseController.check_exist_item(titulo)


    def save_to_database(self, item):
        self.databaseController = ApiRequest()
        self.databaseController.insert_to_database_novas(item)
