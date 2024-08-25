from workout import app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app.config['APPLICATION_ROOT'] = '/workout'

application = DispatcherMiddleware(app, {
    '/workout': app
})

if __name__ == "__main__":
    app.run()