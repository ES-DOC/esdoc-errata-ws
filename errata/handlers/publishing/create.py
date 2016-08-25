# -*- coding: utf-8 -*-

"""
.. module:: handlers.create.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - create issue endpoint.

.. module author:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import sqlalchemy
import tornado

from errata import db
from errata.utils import constants
from errata.utils.http import process_request
from errata.utils.misc import traverse
from errata.utils.validation import validate_url



class CreateIssueRequestHandler(tornado.web.RequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_urls():
            """Validates URL's associated with incoming request.

            """
            for url in traverse([self.request.data.get((i)) for i in ['url', 'materials']]):
                validate_url(url)


        def _set_issue():
            """Creates issue.

            """
            # Map request data to relational data.
            issue = self.issue = db.models.Issue()
            issue.date_closed = self.request.data.get('dateClosed')
            issue.date_created = self.request.data['dateCreated']
            issue.date_updated = self.request.data.get('dateUpdated', issue.date_created)
            issue.description = self.request.data['description']
            issue.institute = self.request.data['institute'].lower()
            issue.materials = ",".join(self.request.data.get('materials', []))
            issue.project = self.request.data['project'].lower()
            issue.severity = self.request.data['severity'].lower()
            issue.title = self.request.data['title']
            issue.uid = self.request.data['uid']
            issue.url = self.request.data.get('url')
            issue.status = self.request.data['status'].lower()


        def _set_datasets():
            """Sets datasets to be persisted to database.

            """
            datasets = self.datasets = []
            for dataset_id in self.request.data['datasets']:
                dataset = db.models.IssueDataset()
                dataset.dataset_id = dataset_id
                dataset.issue_uid = self.issue.uid
                datasets.append(dataset)


        def _set_models():
            """Sets models to be persisted to database.

            """
            models = self.models = []
            for model_id in self.request.data['models']:
                model = db.models.IssueModel()
                model.model_id = model_id
                model.issue_uid = self.issue.uid
                models.append(model)


        def _persist():
            """Persists data to dB.

            """
            # Persist issue data.
            with db.session.create():
                try:
                    db.session.insert(self.issue)
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()
                    raise ValueError("Issue description/uid fields must be unique")

            # Persist datasets / models.
            with db.session.create(commitable=True):
                for dataset in self.datasets:
                    db.session.insert(dataset, False)
                for model in self.models:
                    db.session.insert(model, False)


        # Process request.
        process_request(self, [
            _validate_issue_urls,
            _set_issue,
            _set_datasets,
            _set_models,
            _persist
            ])
