from aiohttp import web

from demos import demo

@demo(["/custom_demo", "/custom_demo/{param}"],
      name="Custom demo example",
      description="""
        This is an example of a custom handler. 
        Members of AIA should only use this when they do complicated things.
      """)
async def custom_demo_example(data, request):
    name = request.match_info.get('param', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)