import sqlite3
import settings

REGIONS = {
    'Краснодарский край': ['Краснодар', 'Кропоткин', 'Славянск'],
    'Ростовская область': ['Ростов', 'Шахты', 'Батайск'],
    'Ставропольский край': ['Ставрополь', 'Пятигорск', 'Кисловодск']
}


def connect_database(sql_req):
    '''
    Main functions for DB interactions.
    :param sql_req: request string (multiple requests must be divided by ';')
    :return: dict {'fetch': cursor.fetchall(), 'lastrowid': cursor.lastrowid}
    '''
    if sql_req is not None:
        with sqlite3.connect(settings.DB_NAME) as connection:
            try:
                cursor = connection.cursor()
                sql_req = sql_req.split(';')
                sql_req.pop()
                for script in sql_req:
                    cursor.execute(script)
                # print('cursor.lastrowid:', cursor.lastrowid)
                # print('cursor.fetchall:', cursor.fetchall())
                response = {'fetch': cursor.fetchall(), 'lastrowid': cursor.lastrowid}
                connection.commit()
                cursor.close()
                return response
            except Exception as err:
                print("Database error: ", err)


def create_database():
    '''
    Initiates DB according to data in REGIONS
    '''
    sql_req = _get_sql_reqv('create_database')
    connect_database(sql_req)
    for region, towns in REGIONS.items():
        add_region(region, towns)


def add_region(region, towns):
    try:
        sql_req = _get_sql_reqv('insert_regions').format(region)
        region_id = connect_database(sql_req)['lastrowid']
        add_towns(region_id, towns)
    except Exception as err:
        print('Database error: add region: ', err)


def add_towns(region_id, towns):
    if not isinstance(region_id, int) or not isinstance(towns, list):
        print('Database wrong request: add towns')
        return
    sql_template = _get_sql_reqv('insert_towns')
    try:
        sql_req = ''.join([sql_template.format(region_id, town) for town in towns])
        connect_database(sql_req)
    except TypeError as err:
        print('Database wrong request: add towns', err)


def post_comment(data):
    if not isinstance(data, dict):
        print('Database wrong request: post comment')
        return
    sql_template = _get_sql_reqv('post_comment')
    try:
        sql_req = sql_template.format(data['region_id'], data['towns_id'], data['user_name'],
                                      data['user_patronim'], data['user_last_name'], data['user_email'],
                                      data['user_phone'], data['comment_content'])
        connect_database(sql_req)
    except TypeError as err:
        print('Database wrong request: post comment', err)


def delete_comment(comm_id):
    sql_req = _get_sql_reqv('delete_comment').format(comm_id)
    connect_database(sql_req)


def get_regions():
    sql_req = _get_sql_reqv('get_regions')
    regions = connect_database(sql_req)['fetch']
    return regions


def get_towns(region_id):
    sql_req = _get_sql_reqv('get_towns').format(region_id)
    towns = connect_database(sql_req)['fetch']
    return towns


def get_comments():
    sql_req = _get_sql_reqv('get_comments')
    comments = connect_database(sql_req)['fetch']
    return comments


def get_region_stat():
    sql_req = _get_sql_reqv('get_region_statistics')
    return connect_database(sql_req)['fetch']


def get_town_stat(r_id):
    sql_req = _get_sql_reqv('get_town_statistics').format(r_id)
    stat = connect_database(sql_req)['fetch']
    sql_req = _get_sql_reqv('get_towns').format(r_id)
    towns = connect_database(sql_req)['fetch']
    try:
        towns = [i[1] for i in towns]
        stat_towns = [k[0] for k in stat]
        for i in towns:
            if i not in stat_towns:
                stat.append((i, 0))
    except (TypeError, ValueError) as err:
        print('Cannot get town stat: ', err)
        return []
    return stat


def _get_sql_reqv(request):
    try:
        with open(settings.SQL_PATH+request+'.sql', 'r') as f:
            sql_req = ''.join(f.readlines())
            return sql_req
    except FileNotFoundError:
        print('Database request file not found')
        return '{}'


