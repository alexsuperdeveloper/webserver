from wsgiref.simple_server import make_server
import re
import views
import settings
import database

urlpatterns = [
    ('/$', views.main_page),
    ('/comment', views.comment_page),
    ('/post_comment', views.post_comment),
    ('/delete_comment', views.delete_comment),
    ('/view', views.view_comments),
    ('/towns', views.get_towns),
    ('/stat_by_region', views.stat_by_region),
    ('/stat', views.view_statistics),
    (settings.STATIC.lower(), views.get_static),
    (r'^.+', views.not_found)
]


def application(environ, start_response):
    inner_path = environ['PATH_INFO'].lower()
    method = environ['REQUEST_METHOD'].upper()
    query_string = environ['QUERY_STRING']
    status = '200 OK'
    headers = [("Content-Type", "text/html")]

    for pattern in urlpatterns:
        if re.match(pattern[0], inner_path):
            view = pattern[1]

            if method == "POST":
                try:
                    request_body = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH', 0)))
                    # print('POST request: ', request_body)
                    response_body = view(request_body)
                except (TypeError, ValueError) as err:
                    print('Post error: ', err)
                    response_body = ''
            else:
                if view == views.get_static:
                    response_body = view(inner_path)
                    if inner_path.endswith('.css'):
                        headers = [("Content-Type", "text/css")]
                    elif inner_path.endswith('.js'):
                        headers = [("Content-Type", "text/javascript")]
                elif query_string:
                    response_body = view(query_string)
                else:
                    response_body = view()
            break

    start_response(status, headers)

    # print('reqv_body:', inner_path)
    # print('response_body:', response_body)

    return [response_body.encode()]


if __name__ == "__main__":
    database.create_database()

    port = 8000
    host = ''
    with make_server(host, port, application) as httpd:
        print(f"Running on {host}:{port}...")
        httpd.serve_forever()
