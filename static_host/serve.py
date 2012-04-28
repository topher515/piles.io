import Image

import bottle
from StringIO import StringIO
from bottle import route, run, request, abort, redirect, static_file, template

@route('/', method='POST')
def file_post():
    print "Simulated file post"
    print request.forms.items()
    print "Reading file with name %s..." % request.files['file'].filename,
    try:
        fileread = request.files['file'].file.read()
        print "Read file successfully"
    except:
        print "Failed to read file!"
    try:
        im = Image.open(StringIO(fileread))
        print "Got image: %s" % im
    except:
        from traceback import print_exc
        print_exc()    
    print "...done reading."
    

@route('/:path#.+#')
def server_static(path):
    '''Serve the staged static files'''
    return static_file(path, root='staged')


def serve():
    app = bottle.default_app()
    run(host='localhost', port=9090, app=app, reloader=False)

if __name__ == '__main__':
    serve()