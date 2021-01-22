import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime


currentDT = datetime.datetime.now()
dia = currentDT.day
mes = currentDT.month
ano = currentDT.year

data_inicial = '2021-01-15'
data_final = '{0}-{1:02d}-{2:02d}'.format(str(ano), mes, dia)



class CustonTools:

    def cleanHTML(self, html):
        # create a new bs4 object from the html data loaded
        soup = BeautifulSoup(html, 'html.parser')

        # remove all javascript and stylesheet code
        for script in soup(["script", "style"]):
            script.decompose()

        # get text
        text = soup.get_text()
        for link in soup.find_all('a'):

            if 'href' in link.attrs:
                repl = link.get_text()

                link.clear()

                link.append(repl)

                text = re.sub(repl + '(?!= *?</a>)', str(link), text, count=1)

        lines = (line.strip() for line in text.splitlines())

        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))

        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def get_key_word_list(self):
        key_word_list = [
            'Covid',
            'Covid-19',
            'Coronavírus'
            'Coronavirus',
            'SARS-CoV-2',
            'Covid19',
            'SRAG',
            'Sindrome Respiratória',
            'Sars',
            'nCov',
            '2019-nCoV',
            'Coronavírus',
            'H1N1',
            'Gripe',
            'Pandemia',
            'Epidemia',
            'Isolamento',
            'antiretroviral',
            'Retroviral',
            'Cloroquina',
            'Hidroxicloroquina',
            'Mascara',
            'Luva',
            'Wuhan',
            'Lombardia',
            'Milão',
            'Madrid',
            'Barcelona',
            'Paris',
            'Londres',
            'Distância social',
            'Confinamento',
            'Confinamento vertical',
            'Isolamento social',
            'Isolamento vertical',
            'Isolamento horizontal']
        return key_word_list

    def check_word_in_html(self, w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def format_dia(self, dia):
        splitedData = dia.split('/')
        dia = splitedData[0]
        mes = splitedData[1]
        ano = splitedData[2]
        if len(ano) <= 2:
            newAno = '20' + ano
            ano = newAno

        data = ano + '-' + mes + '-' + dia
        return data.replace(' ', '')

    def transform_data_g1(self, data):
        if 'hora' or 'horas' or 'minuto' or 'minutos' or 'dia' or 'dias' in data:
            currentDT = datetime.datetime.now()

            data = str(currentDT.year) + '-' + \
                str(currentDT.month) + '-' + str(currentDT.day)
            return data
        else:
            return data

    def format_data_oglobo(self, data):
        matches = ['hora', 'horas', 'minuto', 'minutos', 'dia', 'dias']

        if any(x in data for x in matches):
            currentDT = datetime.datetime.now()
            dia = currentDT.day
            mes = currentDT.month
            ano = currentDT.year

            if dia < 10:
                dia = '0' + str(currentDT.day)

            if mes < 10:
                mes = '0' + str(currentDT.month)

            data = '{0}-{1}-{2}'.format(str(ano), str(mes), str(dia))
            return data
        else:
            newDate = self.format_dia(data.split(' ')[16])
            return newDate

    def format_data_estadao(self, data):

        mesTransform = [
            {'mounth': 'janeiro', 'index': '01'},
            {'mounth': 'fevereiro', 'index': '02'},
            {'mounth': 'março', 'index': '03'},
            {'mounth': 'abril', 'index': '04'},
            {'mounth': 'maio', 'index': '05'},
            {'mounth': 'junho', 'index': '06'},
            {'mounth': 'julho', 'index': '07'},
            {'mounth': 'agosto', 'index': '08'},
            {'mounth': 'setembro', 'index': '09'},
            {'mounth': 'outubro', 'index': '10'},
            {'mounth': 'novembro', 'index': '11'},
            {'mounth': 'dezembro', 'index': '12'}
        ]

        splitedData = data.split(' ')
        dia = splitedData[0]

        for item_mes in mesTransform:
            if item_mes['mounth'] == splitedData[2]:
                mes = item_mes['index']
        ano = splitedData[4]

        data = ano + '-' + mes + '-' + dia
        return data.replace(' ', '')

    def format_data_folhasp(self, data):

        mesTransform = [
            {'mounth': 'jan', 'index': '01'},
            {'mounth': 'fev', 'index': '02'},
            {'mounth': 'mar', 'index': '03'},
            {'mounth': 'abr', 'index': '04'},
            {'mounth': 'mai', 'index': '05'},
            {'mounth': 'jun', 'index': '06'},
            {'mounth': 'jul', 'index': '07'},
            {'mounth': 'ago', 'index': '08'},
            {'mounth': 'set', 'index': '09'},
            {'mounth': 'out', 'index': '10'},
            {'mounth': 'nov', 'index': '11'},
            {'mounth': 'dez', 'index': '12'}
        ]

        splitedData = data.split(' ')
        dia = splitedData[0]

        if dia == '1º':
            dia = '01'
        elif int(dia) < 10:
            dia = '0' + dia

        for item_mes in mesTransform:
            if item_mes['mounth'] == splitedData[1]:
                mes = item_mes['index']
        ano = splitedData[2]

        data = ano + '-' + mes + '-' + dia
        return data.replace(' ', '')

    def clean_html_class_folhasp(self, html):

        soup = BeautifulSoup(html, 'html.parser')
        for div in soup.select('div[class*="rs_skip"]'):
            div.clear()
            div.decompose()

        return str(soup)

    def clean_html_class_oglobo(self, html):

        soup = BeautifulSoup(html, 'html.parser')
        for div in soup.select('div[class*="block__advertising block__advertising-in-text"]'):
            div.clear()
            div.decompose()

        return str(soup)

    def compare_dates(self, noticia_date):
        global data_inicial, data_final

        noticia_date = datetime.datetime.strptime(noticia_date, '%Y-%m-%d')

        data_inicial_com_horas = datetime.datetime.strptime(data_inicial, '%Y-%m-%d')
        data_final_com_horas = datetime.datetime.strptime(data_final, '%Y-%m-%d')

        was_date1_before = data_final_com_horas - noticia_date
        noticia_passou_data_limite = noticia_date <= data_inicial_com_horas            
        #return was_date1_before.days > 12
        return noticia_passou_data_limite
