import json
import requests

import time
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import Session, exceptions

from joao_scrap.tools.databaseController_0 import DataBaseController


class ApiRequest:
    def __init__(self):

        self.database = DataBaseController()

    def make_request(self, router, data):

        if router == 'check_exist_database':
            return self.database.check_exist_item(data)

        return self.database.insert_to_database_novas(data)


# INSERT INTO lacescovid_noticias ( fonte, titulo, descricao, dia, link, tags, noticia) SELECT fonte, titulo, descricao, dia, link, tags, noticia FROM lacescovid_noticias_novas;
# DELETE FROM `lacescovid_noticias_novas`;
# ALTER TABLE lacescovid_noticias_novas AUTO_INCREMENT = 1;


# DELETE FROM noticias WHERE id NOT IN (SELECT * FROM (SELECT MAX(n.id) FROM noticias n GROUP BY n.link) x)
# SET @reset = 0; UPDATE lacescovid_noticias_novas SET id = @reset:= @reset + 1;
# ALTER TABLE lacescovid_noticias_novas AUTO_INCREMENT = 1
# SELECT *, COUNT(*) FROM `lacescovid_noticias_novas` GROUP BY link HAVING COUNT(*) > 1;
