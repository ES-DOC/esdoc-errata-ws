from constants import *
from errata.handle_service.utils import list_children_filenames
from utils import *


class GenericHandleRegister(object):
    """
    entity parsing the handle registry response.
    """
    def __init__(self, handle):
        self.checksum = handle[CHECKSUM]
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]


class DatasetHandleRegister(GenericHandleRegister):
    def __init__(self, handle, handle_client_instance):
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
            self.first = True
        # for child in handle[CHILDREN].split(';'):
        #     self.children.append(child)
        self.children = list_children_handles(handle, handle_client_instance)
        self.id = handle[DRS]
        self.version = handle[VERSION]
        try:
            self.errata = handle[ERRATA_IDS]
            self.has_issue = True
        except KeyError:
            self.has_issue = False

    def get_successor(self, handle_client_instance):
        """
        :param handle_client_instance
        :return successor handle
        """
        return get_handle_by_handle_string(self.successor, handle_client_instance)

    def get_predecessor(self, handle_client_instance):
        """
        :param handle_client_instance
        :return predecessor handle
        """
        return get_handle_by_handle_string(self.predecessor, handle_client_instance)


class FileHandleRegister(GenericHandleRegister):
    def __init__(self, handle, handle_client_instance, parent):
        """
        Needs handle client instance to get parent
        """
        self.filename = handle[FILE_NAME]
        self.parent_handle_string = handle[PARENT]
        if parent is None:
            self.parent_handle = self.get_parent_handle(self, handle_client_instance)
        else:
            self.parent_handle = self.get_parent_handle(self, handle_client_instance)

    def get_parent_handle(self, handle_client_instance):
        """
        :param handle_client_instance: instance of the handle client
        :return: parent handle
        """
        return get_handle_by_handle_string(self.parent_handle_string, handle_client_instance)





