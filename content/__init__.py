from flask import current_app, Flask, redirect, url_for
from flask.ext.cors import CORS

# app = Flask(__name__)
# app.config.from_object('config')



# import content.views

# def create_app(cfg=None):
#     app = Flask(__name__)
#     from api.views import api
#     app.register_blueprint(api)
#     return app

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # TODO - Configure logging
    # if not app.testing:
    #     logging.basicConfig(level=logging.INFO)

    # Setup the data model.
    # with app.app_context():
    #     model = get_model()
    #     model.init_app(app)

    # Register the Bookshelf CRUD blueprint.
    #from .crud import crud
    from content.views import api
    from .views import api
    app.register_blueprint(api, url_prefix='/content')

    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('api.show_resorts'))
        # return "Welcome"

    # Add an error handler. This is useful for debugging the live application,
    # however, you should disable the output of the exception for production
    # applications.
    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    @app.errorhandler(404)
    def page_not_found(e):
        """Return a custom 404 error."""
        return 'Sorry, Nothing at this URL.', 404

    return app

