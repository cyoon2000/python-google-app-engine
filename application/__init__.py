from flask import current_app, Flask, redirect, url_for
from flask.ext.cors import CORS
from flask.ext.triangle import Triangle

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    CORS(app)
    Triangle(app)
    app.config.from_object(config)
    # app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.secret_key = 'some_secret'

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # TODO - Configure logging
    # if not app.testing:
    #     logging.basicConfig(level=logging.INFO)

    with app.app_context():
        from .bookings import get_model
        get_model().init_app(app)
        # run ONLY WHEN needed - create tables, (re)populate data
        get_model().init_db()

    from .contents.views import api
    app.register_blueprint(api, url_prefix='/content')

    from .bookings.views import bookings_api
    app.register_blueprint(bookings_api, url_prefix='/bookings')

    from .bookings.views_example import example_api
    app.register_blueprint(example_api, url_prefix='/example')

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

