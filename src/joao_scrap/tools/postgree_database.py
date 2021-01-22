import psycopg2


def create_connection():
    connection = psycopg2.connect(database="postgres", user="postgres",
                                  password="Postgres2019!", host="localhost", port="15432")

    if connection:

        return connection

    else:
        print('erro ao se conectar ao banco')


class DataBaseController:

    def check_exist_database(self, column, value):

        connection = create_connection()

        try:
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM lacescovid_noticias WHERE  {0}=%s".format(
                    column)
                cursor.execute(sql, (value,))

                result = cursor.fetchone()
                connection.close()

                if result is not None:
                    return True
                else:

                    return False
        except pymysql.MySQLError as e:
            print('erro check exist database novas' + str(e))
        connection.close()

    def check_exist_database_novas(self, column, value):
        connection = create_connection()

        try:

            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT * FROM lacescovid_noticias_novas WHERE {0}=%s".format(
                    column)

                cursor.execute(sql, (
                    value,))

                result = cursor.fetchone()

                connection.close()
                if result is not None:
                    return True
                else:

                    return False
        except Exception as e:
            print('erro check exist database' + str(e))

    def insert_to_database(self, item_noticia):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO lacescovid_noticias (fonte, titulo, descricao, dia, link, tags, noticia) VALUES (%s,%s,%s,%s," \
                      "%s,%s,%s) "
                cursor.execute(sql, (item_noticia['fonte'],
                                     item_noticia['titulo'],
                                     item_noticia['descricao'],
                                     item_noticia['dia'],
                                     item_noticia['link'],
                                     item_noticia['tags'],
                                     item_noticia['noticia']))
                connection.commit()
        except pymysql.MySQLError as e:
            print(e)
        finally:
            connection.close()

    def insert_to_database_novas(self, item_noticia):
        connection = create_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO lacescovid_noticias_novas (fonte, titulo, descricao, dia, link, tags, noticia) VALUES (%s,%s," \
                      "%s,%s,%s,%s,%s) "
                cursor.execute(sql, (item_noticia['fonte'],
                                     item_noticia['titulo'],
                                     item_noticia['descricao'],
                                     item_noticia['dia'],
                                     item_noticia['link'],
                                     item_noticia['tags'],
                                     item_noticia['noticia']))

                connection.commit()
                return True
        except pymysql.MySQLError as e:
            print(e)
        finally:
            connection.close()

    def check_exist_item(self, data):
        column = 'id'
        value = None

        if self.check_exist_database_novas(column, value):
            print('nova: true')

            return True

        elif self.check_exist_database(column, value):
            print('old: true')

            return True
        else:
            return False

# DELETE FROM noticias WHERE id NOT IN (SELECT * FROM (SELECT MAX(n.id) FROM noticias n GROUP BY n.link) x)
# SET @reset = 0; UPDATE noticias SET id = @reset:= @reset + 1;
# SELECT *, COUNT(*) FROM `noticias` GROUP BY link HAVING COUNT(*) > 1;
