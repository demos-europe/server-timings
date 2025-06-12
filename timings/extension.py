import logging

from flask import g

from .models import ServerTimings


class ServerTimingsExtension:
    def __init__(self, app=None):
        self.logger = logging.getLogger(__name__)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        g.timings = ServerTimings()

    def after_request(self, response):
        timing_header = ", ".join(str(metric) for metric in g.timings.metrics)

        if len(timing_header) > 0:
            self.logger.info(g.timings.dumps())
            response.headers["Server-Timing"] = timing_header
            g.timings.discard_all()

        return response
