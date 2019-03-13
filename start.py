import os

import aiohttp_jinja2
import jinja2
from aiohttp import web

from demo_list import demo_handlers

@aiohttp_jinja2.template('index.jinja2')
async def index(request):
    return {
        "demos": demo_handlers,
        "load": os.getloadavg()[2],
    }

app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('tpl'))

routes = [web.get('/', index)]

for func in demo_handlers:
    for path in func.paths:
        # allow most types of requests
        routes.append(web.get(path, func))
        routes.append(web.post(path, func))
        routes.append(web.put(path, func))

app.add_routes(routes)
web.run_app(app)