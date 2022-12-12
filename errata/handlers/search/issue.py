import tornado

from errata import db
from errata.utils import http_security
from errata.utils.http import process_request



# Query parameters.
_PARAM_CRITERIA = 'criteria'


class IssueSearchRequestHandler(tornado.web.RequestHandler):
    """Search issue request handler.

    """
    def set_default_headers(self):
        """Set HTTP headers at the beginning of the request.

        """
        http_security.set_headers(self)


    def get(self):
        """HTTP GET handler.

        """
        def _set_criteria():
            """Sets search criteria.

            """
            self.criteria = self.get_argument(_PARAM_CRITERIA).split(',')


        def _set_data():
            """Pulls data from db.

            """
            with db.session.create():
                self.issues = db.dao.get_issues(self.criteria)
                self.total = db.utils.get_count(db.models.Issue)


        def _set_output():
            """Sets response to be returned to client.

            """
            self.output = {
                'count': len(self.issues),
                'results': self.issues,
                'total': self.total
            }


        # Process request.
        process_request(self, [
            _set_criteria,
            _set_data,
            _set_output
            ])
