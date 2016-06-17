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


class FileHandleRegister(GenericHandleRegister):
    def __init__(self, handle):
        self.filename = handle[FILE_NAME]
        self.parent = handle[PARENT]

    def get_parent_handle(self, handle_client_instance):
        """
        returns handle instance's parent handle.
        :param handle_client_instance: instance of the handle client
        :return: parent handle
        """
        return get_handle_by_handle_string(self.parent, handle_client_instance)


class HandleRegister(object):
    def __init__(self, handle, handle_client):
        if handle[AGGREGATION_LEVEL] == FILE:
            self.handle = FileHandleRegister(handle)
        elif handle[AGGREGATION_LEVEL] == DATASET:
            self.handle = DatasetHandleRegister(handle)




