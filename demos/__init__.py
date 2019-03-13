import asyncio
import functools
import json
from asyncio import subprocess

from aiohttp import web


def demo(paths, name=None, description=None, default_data=None):
    """
    Decorator for a demo. Use this to indicate to the tool how and when it should handle your demo.
    :param paths: the web paths that leads to this web handler. Can be either a string ("/path/to/my/script") or an
                  array of strings.
    :param name: The name of the script. Default: paths[0] if paths is a list or paths if it is a string.
    :param description: The description of the script. Default "".
    :param default_data: Data to send by default (on GET request or empty POST request)
    """
    def inner(func):
        @functools.wraps(func)
        async def wrapped(request):
            body = await request.text()
            if body == "" or body is None:
                body = default_data or {}
            else:
                try:
                   body = json.loads(body)
                except:
                    return web.json_response({"status": "error", "message": "Invalid input. Should be a JSON."})

            return await func(body, request)

        vpaths = [paths] if isinstance(paths, str) else paths
        wrapped.paths = vpaths
        wrapped.name = name if name is not None else vpaths[0]
        wrapped.description = description if description is not None else ""
        wrapped.default_data = default_data

        return wrapped

    return inner

def json_run(command, paths, name=None, description=None, default_data=None, timeout=10.0):
    """
    Runs a command, and expects json at the input and json at the output.
    :param command: str containing the command to run. Will be run in a shell.
    :param paths: the web paths that leads to this web handler. Can be either a string ("/path/to/my/script") or an
                  array of strings.
    :param name: The name of the script. Default: paths[0] if paths is a list or paths if it is a string.
    :param description: The description of the script. Default "".
    :param timeout: a maximum runtime for your demo, as a floating point number in seconds. Default is ten seconds.
    :param default_data: Data to send by default (on GET request or empty POST request)
    """
    @demo(paths, name, description, default_data)
    async def inner(data, request):
        proc = await asyncio.create_subprocess_shell(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
        try:
            to_send = json.dumps(data).encode()
            (stdout, stderr) = await asyncio.wait_for(proc.communicate(to_send), timeout)
            data = json.loads(stdout.decode())

            return web.json_response({"status": "ok", "data": data})
        except asyncio.TimeoutError:
            safekill(proc)
            error = "It took more than {} seconds to solve your data. This server is only for demo purposes, try to" \
                    " run the algorithm on your computer to extend the timeout!.".format(timeout)
        except json.decoder.JSONDecodeError:
            error = "Our tool did not return a correct output. This is a bug on our side. Sorry!"
        except Exception as e:
            safekill(proc)
            error = "An error occured. ({}, {})".format(type(e), e)

        return web.json_response({"status": "error", "message": error})

    return inner

def safekill(proc):
    try:
        proc.kill()
    except:
        pass