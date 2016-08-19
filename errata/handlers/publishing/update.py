# -*- coding: utf-8 -*-

"""
.. module:: handlers.update.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: ES-DOC Errata - update issue endpoint.

.. moduleauthor:: Atef Bennasser <abenasser@ipsl.jussieu.fr>


"""
import difflib

from errata import db
from errata.utils import constants
from errata.utils import exceptions
from errata.utils.http import HTTPRequestHandler



class UpdateIssueRequestHandler(HTTPRequestHandler):
    """issue handler.

    """
    def post(self):
        """HTTP POST handler.

        """
        def _validate_issue_exists():
            """Validates that the issue has been previously posted to the web-service.

            """
            with db.session.create():
                self.issue = db.dao.get_issue(self.request.data['uid'])
            if self.issue is None:
                raise exceptions.UnknownIssueError(self.request.data['uid'])


        def _validate_issue_immutable_attributes():
            """Validates that issue attribute deemed to be immutable have not been changed.

            """
            for attr_name in constants.IMMUTABLE_ISSUE_ATTRIBUTES:
                if unicode(self.request.data[attr_name]).lower() != unicode(getattr(self.issue, attr_name)).lower():
                    raise exceptions.ImmutableIssueAttributeError(attr_name)
            print "TODO: validate dateCreated immutability"


        def _validate_issue_description_change_ratio():
            """Validates that the degree of change in the issue's description is less than allowed ratio.

            """
            # Escape if no change.
            if self.request.data['description'] == self.issue.description:
                return

            # Determine change ratio.
            diff = difflib.SequenceMatcher(None, self.issue.description, self.request.data['description'])
            diff_ratio = round(diff.ratio(), 3) * 100
            if diff_ratio < constants.DESCRIPTION_CHANGE_RATIO:
                raise exceptions.IssueDescriptionChangeRatioError(diff_ratio)


        def _validate_issue_status():
            """Validates that issue state allows it to be updated.

            """
            if self.issue.workflow != constants.WORKFLOW_NEW and \
               self.request.data['workflow'] == constants.WORKFLOW_NEW:
                raise exceptions.InvalidIssueStatusError()


        def _update_issue():
            """Updates issue.

            """
            self.issue.date_closed = self.request.data.get('dateClosed')
            self.issue.date_updated = self.request.data['dateUpdated']
            self.issue.description = self.request.data['description']
            self.issue.materials = ",".join(self.request.data.get('materials', []))
            self.issue.severity = self.request.data['severity'].lower()
            self.issue.state = constants.STATE_CLOSED if self.issue.date_closed else constants.STATE_OPEN
            self.issue.title = self.request.data['title']
            self.issue.url = self.request.data.get('url')
            self.issue.workflow = self.request.data['workflow'].lower()


        def _persist():
            """Persists dB state changes.

            """
            # Perist changes in a single commit.
            with db.session.create(commitable=True):
                # ... update issue.
                db.session.update(self.issue, False)

                # ... delete existing datasets / models.
                db.dao.delete_issue_datasets(self.issue.uid)
                db.dao.delete_issue_models(self.issue.uid)

                # ... insert datasets.
                for dataset_id in self.request.data.get('datasets', []):
                    dataset = db.models.IssueDataset()
                    dataset.dataset_id = dataset_id
                    dataset.issue_uid = self.issue.uid
                    db.session.insert(dataset, False)

                # ... insert models.
                for model_id in self.request.data.get('models', []):
                    model = db.models.IssueModel()
                    model.model_id = model_id
                    model.issue_uid = self.issue.uid
                    db.session.insert(model, False)


        # Invoke tasks.
        self.invoke([
            _validate_issue_exists,
            _validate_issue_immutable_attributes,
            _validate_issue_description_change_ratio,
            _validate_issue_status,
            _update_issue,
            _persist
            ])
