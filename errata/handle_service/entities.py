from constants import *
from errata.handle_service.utils import list_children_filenames
from utils import *


class HandleRegister:
    """
    entity parsing the handle registry response.
    """

    def __init__(self, handle, handle_client_instance):
        self.checksum = handle[CHECKSUM]
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]
        # depending on the aggregation level the object attributes vary
        if self.aggregation == FILE:
            self.filename = handle[FILE_NAME]
            self.parent = handle[PARENT]
        elif self.aggregation == DATASET:
            self.lineage = [False, False]
            try:
                self.successor = handle[SUCCESSOR]
                self.latest = False
                self.lineage[0] = True
            except KeyError:
                self.latest = True
            try:
                self.predecessor = handle[PREDECESSOR]
                self.lineage[1] = True
            except KeyError:
                pass
            for child in handle[CHILDREN].split(';'):
                self.children.append(child)
            self.children = list_children_filenames(handle, handle_client_instance)
            self.id = handle[DRS]
            self.version = handle[VERSION]
            try:
                self.errata = handle[ERRATA_IDS]
                self.has_issue = True
            except KeyError:
                self.has_issue = False

    def get_parent_handle(self, handle_client_instance):
        """
        returns handle instance's parent handle.
        :param handle_client_instance: instance of the handle client
        :return: parent handle
        """
        return get_handle_by_handle_string(self.parent, handle_client_instance)
