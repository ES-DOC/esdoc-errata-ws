# -*- coding: utf-8 -*-

"""
.. module:: handlers.create.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - create issue endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import sqlalchemy

from errata import db
from errata.utils import constants
from errata.utils import exceptions
from errata.utils.http import HTTPRequestHandler
from errata.utils.misc import traverse
from errata.utils.validation import validate_url
from errata.utils.validation import validate_dataset_id



class CreateIssueRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            for url in traverse([self.request.data.get((i)) for i in ['url', 'materials']]):
                try:
                    validate_url(url)
                except exceptions.UnreachableURLError as error:
                    self.throw(error)


        def _validate_dataset_identifiers():
            """Validates dataset identifiers associated with incoming request.

            """
            for dataset_id in self.request.data.get('datasets', []):
                try:
                    validate_dataset_id(dataset_id)
                except exceptions.InvalidDatasetIdentiferError as error:
                    self.throw(error)


        def _validate_request():
            """Validates incoming request prior to processing.

            """
            self.validate_request_json_headers()
            self.validate_request_params(None)
            self.validate_request_body(constants.JSON_SCHEMAS['create'])
            _validate_issue_urls()
            _validate_dataset_identifiers()


        def _persist_issue():
            """Persists issue data to dB.

            """
            # Map request data to relational data.
            issue = db.models.Issue()
            issue.date_closed = self.request.data.get('date_closed')
            issue.date_created = self.request.data['date_created']
            issue.date_updated = self.request.data.get('date_updated', issue.date_created)
            issue.description = self.request.data['description']
            issue.institute = self.request.data['institute'].lower()
            issue.materials = ",".join(self.request.data.get('materials', []))
            issue.project = self.request.data['project'].lower()
            issue.severity = self.request.data['severity'].lower()
            issue.state = constants.STATE_CLOSED if issue.date_closed else constants.STATE_OPEN
            issue.title = self.request.data['title']
            issue.uid = self.request.data['id']
            issue.url = self.request.data.get('url')
            issue.workflow = self.request.data['workflow'].lower()

            # Persist to dB.
            with db.session.create():
                try:
                    db.session.insert(issue)
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()
                    raise ValueError("Issue description/uid fields must be unique")
                else:
                    self.issue = issue


        def _persist_datasets():
            """Persists dataset data to database.

            """
            # Map request data to relational data.
            datasets = []
            for dataset_id in self.request.data.get('datasets', []):
                dataset = db.models.IssueDataset()
                dataset.dataset_id = dataset_id
                dataset.issue_id = self.issue.id
                datasets.append(dataset)

            # Persist to dB.
            with db.session.create():
                for dataset in datasets:
                    db.session.insert(dataset)


        # Invoke tasks.
        self.invoke([
            _validate_request,
            _persist_issue,
            _persist_datasets
            ])
