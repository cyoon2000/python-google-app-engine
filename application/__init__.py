from flask import current_app, Flask, redirect, url_for
from flask.ext.cors import CORS
#from application.sample import model_cloudsql
from application.sample import get_model

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

    with app.app_context():
        model = get_model()
        model.init_app(app)

    from application.views import api
    from .views import api
    app.register_blueprint(api, url_prefix='/content')

    from application.sample.views import sample
    from sample.views import sample
    app.register_blueprint(sample, url_prefix='/sample')

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
