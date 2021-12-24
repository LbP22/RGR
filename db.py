import pymysql


def sql(request):
    dataBase = pymysql.connect(host="127.0.0.1", user="mysql", database="cinema")
    cur = dataBase.cursor()
    cur.execute(request)
    dataBase.commit()
    dataBase.close()
    return cur


def max_film_id():
    req = "SELECT MAX(film_id) FROM film"
    data = sql(req)
    for row in data:
        return row[0]


def show_products(login):
    req = "SELECT user_prod_id FROM users WHERE user_name = '" + login + "'"
    data = sql(req)
    for row in data:
        return row[0]


def show_genres():
    req = "SELECT genre_id, genre_name FROM genre"
    data = sql(req)
    genres = list()
    for row in data:
        genres.append(list(row))
    return list(genres)


def show_all_authors():
    req = "SELECT * from director"
    data = sql(req)
    films = list()
    for row in data:
        films.append(row)
    return films


def show_all_films():
    req = "SELECT * from film"
    data = sql(req)
    films = list()
    for row in data:
        films.append(row)
    return films


def find_film_info(gen, author):
    req_gen = "SELECT genre_name FROM genre WHERE genre_id = '" + str(gen) + "'"
    req_author = "SELECT director_name FROM director WHERE director_id = '" + str(author) + "'"

    req_gen = sql(req_gen)
    for row in req_gen:
        req_gen = row
    req_gen = req_gen[0]

    req_author = sql(req_author)
    for row in req_author:
        req_author = row
    req_author = req_author[0]

    return [req_gen, req_author]


def find_author(name):
    req = "SELECT * from director WHERE director_name = '" + name + "'"
    data = sql(req)
    for row in data:
        return [True, list(row)]
    return [False, None]


def find_film(name):
    req = "SELECT * from film WHERE film_name = '" + name + "'"
    data = sql(req)
    for row in data:
        return [True, list(row)]
    return [False, None]


def check_log(login):
    req = "SELECT user_name, user_password FROM users"
    data = sql(req)
    for row in data:
        if row[0] == login:
            return [True, row[1]]
    return [False, None]


def check_pas(pas):
    req = """SELECT user_password FROM users"""
    data = sql(req)
    for row in data:
        for word in row:
            if word == pas:
                return True
    return False


def check_mail(mail):
    req = """SELECT user_email FROM users"""
    data = sql(req)
    for row in data:
        for word in row:
            if word == mail:
                return True
    return False


def addUser(name, pas, mail):
    idList = sql("SELECT MAX(user_id) FROM users")
    maxId = int()
    for row in idList:
        maxId = row[0]
    maxId += 1
    req = "INSERT users(user_id, user_name, user_password, user_email, user_prod_id) VALUES " \
          "(" + str(maxId) + ", '" + name + "', '" + pas + "', '" + mail + "', NULL);"
    sql(req)
    return True


def addAuthor(name, desc):
    idList = sql("SELECT MAX(director_id) FROM director")
    maxId = int()
    for row in idList:
        maxId = row[0]
    maxId += 1
    req = "INSERT director(director_id, director_name, director_desc) VALUES " \
          "(" + str(maxId) + ", '" + name + "', '" + desc + "');"
    sql(req)
    return maxId


def addFilm(name, genre, director, trilogy, price):
    idList = sql("SELECT MAX(film_id) FROM film")
    maxId = int()
    for row in idList:
        maxId = row[0]
    maxId += 1

    if trilogy is None:
        trilogy = "NULL"

    req = "INSERT film(film_id, film_name, film_genre_id, film_director_id, film_trilogy, film_price) VALUES " \
          "(" + str(maxId) + ", '" + name + "', '" + str(genre) + "', '" + str(director) + "', '"\
          + trilogy + "', '" + price + "');"
    sql(req)
    return maxId


def addProducts(newProdList, login):
    req1 = "SELECT user_prod_id FROM users WHERE user_name = '" + login + "'"
    data = sql(req1)
    oldList = list()
    for row in data:
        oldList.append(row[0])
    if oldList[0] is None:
        oldList = list()
    for i in list(newProdList):
        oldList.append(int(i))
    req2 = "UPDATE `users` SET `user_prod_id` = '" + str(oldList) + "' WHERE `users`.`user_name` = '" + login + "';"
    sql(req2)


