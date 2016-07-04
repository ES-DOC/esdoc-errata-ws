from utils import *
import logging
from entities import *


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=os.path.join("/home/abennasser", "logs/errata.log"),
                    filemode='w')


def crawler_v1(input_handle, input_handle_string, handle_client_instance):
    """
    Crawls up the tree on a dataset aggregation level. Can also manage on file level.
    :param input_handle: Dataset or file Handle
    :param handle_client_instance: EUDATClient instance
    :param input_handle_string: handle string to be searched
    :return: list of couples [(dataset_handler/file_handler, issue_identifier)], initial dset/file_id
    """
    # initializing return list
    list_of_uids = dict()
    # resolving whether the user input is on a file level or a dataset level.
    aggregation_level = get_aggregation_level(input_handle)
    order_index = 0
    is_file = False
    incomplete_retracing = False
    if aggregation_level == FILE:
        initial_file_handle_register = FileHandleRegister(input_handle, handle_client_instance, None)
        #TODO investigate if we need file errata initialization
        # list_of_uids[initial_file_handle_register.id] = [initial_file_handle_register.parent_handle.errata,
        #                                                  initial_file_handle_register.parent_handle.id,
        #                                                  initial_file_handle_register.parent_handle.version,
        #                                                  order_index]
        is_file = True
    elif aggregation_level == DATASET:
        initial_dataset_handle_register = DatasetHandleRegister(input_handle, handle_client_instance)
        list_of_uids[initial_dataset_handle_register.handle_string] = [initial_dataset_handle_register.errata,
                                                                       initial_dataset_handle_register.id,
                                                                       initial_dataset_handle_register.version,
                                                                       order_index]
    else:
        raise UnresolvedAggregationLevel
    logging.debug('THE HANDLE PROVIDED IS OF AN AGGREGATION LEVEL ' + aggregation_level)
    logging.debug('THE REGISTRY OF APPROPRIATE AGGREGATION HAS BEEN CREATED SUCCESSFULLY...')
    if is_file:
        _dataset_handle = initial_file_handle_register.parent_handle
        _file_handle = initial_file_handle_register
        initial_id = initial_file_handle_register.id
        initial_dataset_handle_register = _dataset_handle
    else:
        _dataset_handle = initial_dataset_handle_register
        initial_id = initial_dataset_handle_register.id
    is_latest = _dataset_handle.latest
    has_issue = _dataset_handle.has_issue
    lineage = _dataset_handle.lineage
    logging.debug("LINEAGE TEST YIELDED ")
    logging.debug(lineage)
    if lineage[0]:
        logging.debug('STARTING UPWARDS CRAWLER...')
        next_lineage = lineage
        # if the aggregation level is file, we got up to the dataset level.
        while _dataset_handle is not None and next_lineage[0]:
            try:
                logging.debug("GETTING PREDECESSOR...")
                predecessor = DatasetHandleRegister(_dataset_handle.predecessor, handle_client_instance,
                                                    successor=_dataset_handle.handle)
                next_lineage = predecessor.lineage
                logging.debug("PREDECESSOR FOUND WITH THE FOLLOWING LINEAGE ")
                logging.debug(next_lineage)
                order_index -= 1
                # Setting the errata information depends on whether we are on
                # dataset or file aggregation level.
                # list_of_uids[predecessor.id] = [predecessor.errata, order_index]
                if is_file:
                    try:
                        _file_handle, errata = find_file_within_dataset(_dataset_handle, _file_handle, PREDECESSOR)
                        _file_handle = FileHandleRegister(_file_handle, handle_client_instance, None)
                        if errata is not None:
                            list_of_uids[_file_handle.parent_handle.handle_string] = [errata, _file_handle.parent_handle.id,
                                                                                      _file_handle.parent_handle.version,
                                                                                      order_index]
                    except FileNotFoundInSuccessor:
                        logging.debug("FILE SEEMS TO HAVE BEEN CREATED IN THIS DATASET...")
                        incomplete_retracing = True
                elif not is_file:

                    list_of_uids[predecessor.handle_string] = [predecessor.errata, predecessor.id, predecessor.version,
                                                               order_index]
            except HandleNotFoundException:
                logging.debug('A LOOKUP FOR A PREVIOUS HANDLE HAS FAILED FOR THE HANDLE ' + predecessor)
                break
            _dataset_handle = predecessor
            lineage = next_lineage
        logging.debug('EXITING UPWARDS CRAWLER...')

    # Reinitializing handle in case it got modified in the process of finding a predecessor
    logging.debug('UPWARDS LOOP HAS BEEN COMPLETED, HANDLE IS NOW RESTORED TO START LEVEL AS WELL AS THE ORDER INDEX...')
    _dataset_handle = initial_dataset_handle_register
    order_index = 0
    if lineage[1]:
        logging.debug('STARTING DOWNWARDS CRAWLER...')
        next_lineage = _dataset_handle.lineage
        while _dataset_handle is not None and next_lineage[1]:
            try:
                logging.debug("FINDING SUCCESSOR...")
                successor = DatasetHandleRegister(_dataset_handle.successor, handle_client_instance,
                                                  predecessor=_dataset_handle.handle)
                next_lineage = successor.lineage
                logging.debug("SUCCESSOR FOUND WITH THE FOLLOWING LINEAGE")
                logging.debug(next_lineage)
                order_index += 1
                if is_file:
                    try:
                        raw_handle, errata = find_file_within_dataset(_dataset_handle, _file_handle, SUCCESSOR)
                        _file_handle = FileHandleRegister(raw_handle, handle_client_instance, _dataset_handle)
                        if errata is not None:
                            logging.debug('AN ISSUE HAS BEEN DETECTED, FILLING LIST...')
                            list_of_uids[_file_handle.parent_handle.handle_string] = [errata, _file_handle.parent_handle.id,
                                                                                       _file_handle.parent_handle.version, order_index]
                    except FileNotFoundInSuccessor:
                        logging.warn("COULD NOT DEDUCE FURTHER ERRATA HISTORY SINCE FILE "
                                     "DISAPPEARED IN SUCCESSOR...")
                        incomplete_retracing = True
                        # in case one failure of finding files is disregarded remove the break.
                        break
                elif not is_file:
                    list_of_uids[successor.handle_string] = [successor.errata, successor.id, successor.version,
                                                             order_index]
            except HandleNotFoundException:
                logging.debug('A LOOKUP FOR A SUCCESSOR HANDLE HAS FAILED' + _dataset_handle.successor[DRS])
                break
            _dataset_handle = successor
            next_lineage = successor.lineage
        logging.debug('EXITING DOWNWARDS CRAWLER...')

    return list_of_uids, initial_id, is_latest, has_issue, incomplete_retracing
