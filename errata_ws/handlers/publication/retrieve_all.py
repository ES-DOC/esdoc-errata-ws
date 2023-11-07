import tornado

from errata_ws import db
from errata_ws.utils import http_security
from errata_ws.utils.http import process_request



class RetrieveAllErrataRequestHandler(tornado.web.RequestHandler):
    """Publishing retrieve all issues handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        http_security.set_headers(self, False)


    def get(self):
        """HTTP GET handler.

        """
        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_all_errata()
                self.resources = db.dao.get_resources()
                self.facets = db.dao.get_facets()


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'issues': [i.to_dict(self.resources, self.facets) for i in self.issues]
            }


        # Process request.
        process_request(self, [
            _set_data,
            _set_output
            ])
