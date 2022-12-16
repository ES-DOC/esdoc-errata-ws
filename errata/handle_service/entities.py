from errata.handle_service.constants import *
from errata.handle_service.exceptions import *
from errata.handle_service.utils import get_handle_by_handle_string, make_handle_from_drsid_and_versionnumber
from errata.utils import logger


class Record(object):
    """Entity parsing the handle registry response.

    """
    def __init__(self):
        """Instance constructor.

        """
        self.checksum = None
        self.url = None
        self.aggregation = None


class DatasetRecord(Record):
    """TODO - descirbe class.

    """
    def __init__(self, handle, handle_client_instance, **kwargs):
        """Instance constructor.

        """
        self.successor = None
        self.predecessor = None
        self.children = None
        self.is_first = False
        self.is_latest = False
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]
        self.lineage = [False, False]
        logger.log('Checking successor and/or predecessor.')
        self.check_descendants(handle, handle_client_instance, **kwargs)
        logger.log('Successor and/or predecessor established.')
        self.id = handle[DRS]
        self.version = handle[VERSION]
        self.errata = None
        try:
            self.errata = handle[ERRATA_IDS]
            self.has_issue = True
        except KeyError:
            self.has_issue = False
        self.handle_string = make_handle_from_drsid_and_versionnumber(prefix=PORT, drs_id=self.id,
                                                                      version_number=self.version)
        self.handle = handle

    def check_descendants(self, handle, handle_client_instance, **kwargs):
        """
        This function checks whether the handle record of the previous and next dataset exists in loop or not.
        If it exists we recycle the data rather than querying the handle service.
        If not it's inevitable to get it from the HS.
        :param handle:
        :param handle_client_instance:
        :param kwargs:
        """
        for direction in ['successor', 'predecessor']:
            if direction not in kwargs:
                try:
                    logger.log('Retrieving {} for dataset record...'.format(direction))
                    try:
                        if direction == 'successor':
                            self.successor = get_handle_by_handle_string(handle[SUCCESSOR].replace(HDL_PREFIX, ''),
                                                                         handle_client_instance)
                            self.is_latest = False
                            self.lineage[1] = True
                        else:
                            self.predecessor = get_handle_by_handle_string(handle[PREDECESSOR].replace(HDL_PREFIX, ''),
                                                                           handle_client_instance)
                            self.lineage[0] = True
                    except HandleNotFoundError:
                        logger.log_warning('{} handle was not found in handle server.'.format(direction))
                    logger.log('{} successfully retrieved.'.format(direction))
                except KeyError:
                    if direction == 'successor':
                        self.is_latest = True
                    else:
                        self.is_first = True
            else:
                logger.log('Retrieving {} from previous loop.'.format(direction.upper()))
                if direction == 'successor':
                    self.successor = kwargs[direction]
                    self.is_latest = False
                    self.lineage[1] = True
                else:
                    self.predecessor = kwargs[direction]
                    self.lineage[0] = True
                logger.log('{} from previous loop successfully retrieved.'.format(direction.upper()))

    def get_children_handles(self, handle_client_instance):
        """Lists children from dataset.
        :param handle_client_instance: EUDATClient instance

        :returns: list of child handle registers contained in dataset
        :rtype: list

        """
        list_of_children = []
        if CHILDREN in self.handle.keys():
            for child in map(lambda x: x.replace(HDL_PREFIX, ''), self.handle[CHILDREN].split(';')):
                child_handle = get_handle_by_handle_string(child, handle_client_instance)
                list_of_children.append(child_handle)
        self.children = list_of_children


class FileRecord(Record):
    """TODO - describe class.

    """
    def __init__(self, handle, handle_client_instance):
        """Instance constructor.

        """
        self.checksum = handle[CHECKSUM]
        self.url = handle[URL]
        self.aggregation = handle[AGGREGATION_LEVEL]
        self.filename = handle[FILE_NAME]
        self.parents = map(lambda x: x.replace(HDL_PREFIX, ''), handle[PARENTS].split(';'))
        self.get_parent_list(handle_client_instance)
        self.id = handle[FILE_NAME]
        self.handle = handle
        self.is_latest = False
        self.is_first = False
        self.errata = None
        if FILE_VERSION in handle.keys():
            self.version = handle[FILE_VERSION]

    def get_parent_list(self, handle_client_instance):
        """Returns an ordered list of parents
        :param handle_client_instance: instance of the handle client
        :returns: parent handle

        """
        parents = []
        for parent in self.parents:
            parents.append(DatasetRecord(get_handle_by_handle_string(parent, handle_client_instance),
                                         handle_client_instance))
        for i, parent in enumerate(parents):
            if parent.successor in parents and parent.successor.index() != i+1:
                var = parents[i+1]
                parents[parent.successor.index()] = var
                parents[i+1] = parent.successor
            elif parent.predecessor in parents and i > 0 and parent.predecessor.index() != i-1:
                var = parents[i-1]
                parents[parents.predecessor.index()] = var
                parents[i-1] = parent.predecessor
        self.parents = parents
