import logging

from flask import g

from flask import request

from timings.models import ServerTimings


class ServerTimingsExtension:
    def __init__(self, app=None):
        self.logger = logging.getLogger(__name__)

        if not self.logger.hasHandlers():
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s %(path)s %(timings)s %(message)s"
            )
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)

    def before_request(self):
        # Bind sync storage for this request
        ServerTimings.setUp("sync")
        g.timings = ServerTimings()

    def after_request(self, response):
        timing_header = ", ".join(str(metric) for metric in g.timings.metrics)
        if len(timing_header) > 0:
            self.logger.info(
                msg="Server timings",
                extra={"path": request.path, "timings": g.timings.dump()},
            )
            response.headers["Server-Timing"] = timing_header
            g.timings.discard_all()

        return response
    
    def teardown_request(self, exception):
        # Clean up storage after request
        ServerTimings.tearDown()
