'''Request scope middleware for WSGI and Django applications. It registers
and unregisters a thread-local storage for each request.
'''
import inject.scopes


class WsgiInjectMiddleware(object):
    
    '''WSGI inject middleware registers a request scope for each request,
    and unregisters it after returning the response.
    
    @warning: WSGI inject middleware requires Python2.5+ because the later
        versions do not support yield inside a try...finally statement.
    
    '''
    
    scope = inject.class_attr(inject.scopes.RequestScope)
    
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        scope = self.scope
        try:
            scope.start()
            # We have to manually iterate over the response,
            # so that all its parts have been generated before
            # the request is unregistered.
            for s in iter(self.app(environ, start_response)):
                yield s
        finally:
            scope.end()
