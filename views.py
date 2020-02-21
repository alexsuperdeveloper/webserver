from os import path
import settings
import database
import json
import re
from urllib.parse import parse_qs as parser


def _redir(path='/'):
    if path == '/':
        return comment_page()
    elif path == '/view':
        return view_comments()
    else:
        return not_found()


def main_page():
    return _redir()


def post_comment(request_body):
    '''
    Add comment to DB
    '''
    comment = parser(request_body.decode(), True)
    try:
        data = {
            'region_id': int(comment['region_id'][0]),
            'towns_id': int(comment['town_id'][0]),
            'user_name': str(comment['user_name'][0]),
            'user_patronim': str(comment['user_patronim'][0]),
            'user_last_name': str(comment['user_last_name'][0]),
            'user_email': str(comment['user_email'][0]),
            'user_phone': str(comment['user_phone'][0]),
            'comment_content': str(comment['comment_content'][0])
            }
        database.post_comment(data)
    except (TypeError, KeyError) as err:
        print('Cannot parse comment: ', err)
    return _redir('/view')


def comment_page():
    try:
        with open(path.join(settings.TEMPLATES, 'add_comment.html')) as html:
            html = '\n'.join(html.readlines())
            html = html.replace('{% regions %}', get_regions())
            html = html.replace('{% static %}', settings.STATIC)
    except FileNotFoundError as err:
        print('Comment page template no found: ', err)
        html = ''
    return html


def view_comments():
    try:
        with open(path.join(settings.TEMPLATES, 'comment_view.html')) as html:
            html = '\n'.join(html.readlines())
            html = html.replace('{% static %}', settings.STATIC)
            comments = get_comments()
            if not comments:
                html = html.replace('{% content %}',
                                    '<div style="text-align:center; font-size: 25px;">'
                                    ' <b> Комментариев ещё нет </b> </div>')
            else:
                html = html.replace('{% content %}', comments)
    except FileNotFoundError as err:
        print('Comment view page template no found: ', err)
        html = ''
    return html


def view_statistics():
    try:
        with open(path.join(settings.TEMPLATES, 'comment_view.html')) as html:
            html = '\n'.join(html.readlines())
            html = html.replace('{% static %}', settings.STATIC)
    except FileNotFoundError as err:
        print('Statistics page template no found: ', err)
        return ''
    statistics = get_statistic()
    if statistics:
        try:
            with open(path.join(settings.TEMPLATES, 'statistics_template.html')) as template:
                template = '\n'.join(template.readlines())
        except FileNotFoundError as err:
            print('Statistics page template no found: ', err)
            return ''
        content = ''
        for i in statistics:
            content += f'<tr style="text-align:left; vertical-align: center;">' \
                       f'<td > <a href="/stat_by_region/?id={i[0]}"> {i[1]} </a> </td> <td> {i[2]} </td> ' \
                       f'</tr>'
        content = template.replace('{% stat %}', content)
        html = html.replace('{% content %}', content)
    else:
        html = html.replace('{% content %}', '<div style="text-align:center; font-size: 25px;">'
                                             '<b> Нет регионов, в которых больше 5 комментариев </b> </div>')
    return html


def stat_by_region(query):
    try:
        query = parser(query)
        region_id = int(query['id'][0])
        comments_by_towns = get_statistic(region_id)
    except (TypeError, ValueError, IndexError) as err:
        print('Cannot get stat by region: ', err)
        return ''

    try:
        with open(path.join(settings.TEMPLATES, 'comment_view.html')) as html:
            html = '\n'.join(html.readlines())
            html = html.replace('{% static %}', settings.STATIC)
    except FileNotFoundError as err:
        print('Statistics page template no found: ', err)
        return ''

    try:
        with open(path.join(settings.TEMPLATES, 'statistics_template.html')) as template:
            template = '\n'.join(template.readlines())
            template = template.replace('Регион', 'Город')
    except FileNotFoundError as err:
        print('Statistics page template no found: ', err)
        return ''

    content = ''
    try:
        if comments_by_towns:
            for i in comments_by_towns:
                content += f'<tr style="text-align:left; vertical-align: center;">' \
                           f'<td > {i[0]} </a> </td> <td> {i[1]} </td> ' \
                           f'</tr>'
            content = template.replace('{% stat %}', content)
            html = html.replace('{% content %}', content)
        else:
            html = html.replace('{% content %}', '<div style="text-align:center; font-size: 25px;">'
                                                 '<b> Не удалось выполнить запрос </b> </div>')
    except (TypeError, ValueError, IndexError) as err:
        print('Cannot get stat by region: ', err)
        return ''
    return html


def get_statistic(r_id=None):
    if r_id:
        stat = database.get_town_stat(r_id)
    else:
        stat = database.get_region_stat()
    return stat


def not_found():
    try:
        with open(path.join(settings.TEMPLATES, 'comment_view.html')) as html:
            html = '\n'.join(html.readlines())
            html = html.replace('{% content %}',
                                '<div style="text-align:center; font-size: 25px;"> <b> 404 Page not found </b> </div>')
            html = html.replace('{% static %}', settings.STATIC)
    except FileNotFoundError as err:
        print('404 page template no found: ', err)
        html = ''
    return html


def get_comments():
    try:
        comments = database.get_comments()
        html = ''
        with open(path.join(settings.TEMPLATES, 'comment_template.html')) as template:
            template = '\n'.join(template.readlines())
            for comm in comments:
                html = html + '\n' + template.format(
                                                comment_id=comm[0],
                                                region=comm[1],
                                                town=comm[2],
                                                name=comm[3],
                                                patronim=comm[4],
                                                lastname=comm[5],
                                                email=comm[6],
                                                telephone='+7'+comm[7] if comm[7] else '',
                                                comment=comm[8],
                                                datetime=comm[9]
                )
        return html
    except (TypeError, ValueError, FileNotFoundError) as err:
        print('cannot get comment list. ', err)
        return ''


def delete_comment(query):
    try:
        query = parser(query)
        comm_id = int(query['id'][0])
        database.delete_comment(comm_id)
        # print(f'del comment #{comm_id}')
        return _redir('/view')
    except (TypeError, ValueError, IndexError) as err:
        print('Cannot delete comm: ', err)


def get_regions():
    '''
    Gets list of region's tuples, format (region_d, name) from DB. Transforms it into HTML form
    '''
    try:
        regions = database.get_regions()
        html = '\n'.join([f"<option value='{region[0]}'>{region[1]}</option>" for region in regions])
        return html
    except Exception as err:
        print('cannot get towns list. ', err)


def get_towns(request):
    '''
    Gets list of towns's tuples, format (town_id, name) from DB. Transforms it into HTML form
    '''
    try:
        region_id = int(json.loads(request)['region_id'])
        towns = database.get_towns(region_id)
        html = '\n'.join([f"<option value='{town[0]}'>{town[1]}</option>" for town in towns])
        return html
    except Exception as err:
        print('cannot get towns list. ', err)


def get_static(inner_path):
    """
    GET request for js and css files from static folder
    """
    if re.match(settings.STATIC.lower(), inner_path):
        inner_path = re.sub(settings.STATIC.lower(), settings.STATIC, inner_path)
        try:
            with open(inner_path, 'r') as f:
                content = '\n'.join(f.readlines())
            return content
        except FileNotFoundError as err:
            print('Cannot get static file: ', err)
