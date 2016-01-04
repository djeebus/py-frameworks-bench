import aiohttp
import asyncio
import os
import peewee
import peewee_async

HOST = os.environ.get('THOST', '127.0.0.1')

database = peewee_async.PooledPostgresqlDatabase(
    'benchmark', host=HOST, max_connections=10,
    user='benchmark', password='benchmark')


class Message(peewee.Model):
    content = peewee.CharField(max_length=512)

    class Meta:
        database = database


from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='json', renderer='json')
def json(request):
    return {'message': 'Hello, World!'}


@view_config(route_name='remote')
@asyncio.coroutine
def remote(request):
    response = yield from aiohttp.request('GET', 'http://%s' % HOST)
    text = yield from response.text()
    return Response(text)


@view_config(route_name='complete', renderer='template.jinja2')
@asyncio.coroutine
def complete(request):
    messages = yield from peewee_async.execute(Message.select())
    messages = list(messages)
    messages.append(Message(content='Hello, World!'))
    messages.sort(key=lambda m: m.content)
    return {
        'messages': messages
    }


config = Configurator()
config.include('aiopyramid')
config.include('pyramid_jinja2')

config.add_route('json', '/json')
config.add_route('remote', '/remote')
config.add_route('complete', '/complete')

config.scan()

app = config.make_wsgi_app()

# pylama:ignore=E402
