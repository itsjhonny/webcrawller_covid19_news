import scrapy
from joao_scrap.tools.cleanHTML import CustonTools
from joao_scrap.tools.apiController import ApiRequest
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from dicttoxml import dicttoxml
from webdriver_manager.chrome import ChromeDriverManager
from scrapy import Spider, Request


class QuotesSpider(scrapy.Spider):
    name = "get_gauchazh"
    start_urls = [
        'https://scrapy.org',

    ]

    def __init__(self):
        self.arrayNoticias = []
        self.indexData = 0
        chrome_options = Options()
        chrome_options.add_argument("user-data-dir=selenium")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--ignore-certificate-errors')
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(),options=chrome_options)
        self.driver2 = webdriver.Chrome(
            ChromeDriverManager().install(),  options=chrome_options)

    def parse(self, link):

        self.driver.get(
            'https://gauchazh.clicrbs.com.br/search/?q=coronavirus')
        clickButtonNexPage = True

        
        while(clickButtonNexPage):
            try:
                nextPage_button = self.driver.find_element_by_xpath(
                    "//button[@class='btn-show-more']")
                self.driver.execute_script("arguments[0].click();", nextPage_button)
                time.sleep(2)
            except:
                clickButtonNexPage = False
                print('carregou todas as noticias')
                response = self.driver.find_element_by_xpath(
                    "//div[@class='search-results']").find_elements_by_tag_name('ul')[1].find_elements_by_tag_name('div')
                for item in self.get_data(response):
                    if self.check_exist_database(item['link']) == False:
                        print('NOVA ' + item['titulo'])
                        self.extract_html(item)
                pass
    def get_data(self, response):
        for li in response:
            if li.get_attribute('id'):
                yield {

                    'fonte': 'https://gauchazh.clicrbs.com.br',
                    'titulo': li.find_element_by_tag_name('a').find_element_by_class_name('m-headline').text,
                    'descricao': li.find_element_by_class_name('support-text').text,
                    'dia': li.find_element_by_tag_name('time').get_attribute('textContent').split()[0],
                    'link': li.find_element_by_tag_name('a').get_attribute('href'),
                    'noticia': None,
                    'tags': None
                }

    def extract_html(self, item):
        self.driver2.get(item['link'])
        tools = CustonTools()
        wordList = tools.get_key_word_list()
        tags = []
        formatedData = tools.format_dia(item['dia'])
        item['dia'] = formatedData
        try:
            print()
            print()
            print(item['link'])
            #html = self.driver2.find_element_by_xpath("//div[@class='article-content sa_incontent']").get_attribute('innerHTML')
            time.sleep(2)
            html = self.driver2.find_element_by_xpath("//div[@class='article-content sa_incontent']").get_attribute('innerHTML')
        except:
            print('falhou')
            return

        wordList = tools.get_key_word_list()
        tags = []
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
                item['noticia'] = tools.cleanHTML(html)
                #print(item)
                #print('limpou noticia')
                #print('vai salvar no banco')
                self.save_to_database_novas(item)
                #print('chegou ao final do extract html')
            except:
                #print('erro na noticia: ' + item['link'])
                pass
        else:
            print('Noticia não possui tags ' + item['link'])
        return item

    def check_exist_database(self, titulo):
        self.databaseController = ApiRequest()
        return self.databaseController.check_exist_database(titulo)

    def save_to_database(self, item):
        self.databaseController = ApiRequest()
        self.databaseController.insert_to_database(item)
