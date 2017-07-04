# -*- coding: utf-8 -*-
"""
.. module:: handle_service.crawler.py
   :license: GPL/CeCIL
   :platform: Unix
   :synopsis: Handle service dataset aggregation crawler.

.. moduleauthor:: Atef Ben Nasser <abennasser@ipsl.jussieu.fr>


"""
from errata.handle_service.utils import *
from errata.handle_service.entities import *
from errata.utils import logger



def crawler(input_handle, handle_client_instance):
    """Crawls up the tree on a dataset aggregation level. Can also manage on file level.

    :param input_handle: Dataset or file Handle
    :param handle_client_instance: EUDATClient instance
    :returns: dictionary {dataset_handle: (errata_id, dset_id, dset_version, order)}
    :rtype: dict
    """
    incomplete_retracing = 0
    output = dict()
    order_index = 0
    unchanged_file = 0
    aggregation_level = get_aggregation_level(input_handle)
    logger.log('Received {} level handle, processing...'.format(aggregation_level))
    if aggregation_level == FILE:
        file_record = FileRecord(input_handle, handle_client_instance)
        list_of_files = [file_record]
        for dset in file_record.parents:
            if len(file_record.parents) > 1:
                unchanged_file = 1
            output[dset.handle_string] = [file_record.parents[-1].errata, file_record.filename, dset.version, order_index, 0, 0, unchanged_file]

        while file_record.parents[0].lineage[0]:
            logger.log('First file parent has a predecessor, investigating.')
            order_index -= 1
            dataset_record = file_record.parents[0]
            unchanged_file = 0
            predecessor = DatasetRecord(dataset_record.predecessor, handle_client_instance, successor=dataset_record)
            logger.log('Processing predecessor #{} found from first parent #{}'.format(predecessor.version,
                                                                                       dataset_record.version))
            try:
                list_of_files.append(file_record)
                predecessor.get_children_handles(handle_client_instance)
                file_record = FileRecord(find_file_in_dataset(predecessor, file_record), handle_client_instance)
                if len(file_record.parents) > 1:
                    unchanged_file = 1
                logger.log('file record has {} parents'.format(len(file_record.parents)))
                for dset in file_record.parents:
                    output[dset.handle_string] = [predecessor.errata, file_record.filename, dset.version, order_index, 0, 0, unchanged_file]
            except FileNotFoundInHandle as e:
                incomplete_retracing = 1
                logger.log(e.message)
                break
        # output[dset.handle_string] = [predecessor.errata, dset.id, dset.version, order_index, 1, 0]

        # Reinitializing
        order_index = 0
        file_record = list_of_files[0]
        unchanged_file = 0
        while file_record.parents[-1].lineage[1]:
            logger.log('Last file parent has a successor, investigating.')
            order_index += 1
            dataset_record = file_record.parents[-1]
            successor = DatasetRecord(dataset_record.successor, handle_client_instance, predecessor=dataset_record)
            logger.log('Processing successor #{} found from last parent #{}'.format(successor.version,
                                                                                    dataset_record.version))
            try:
                successor.get_children_handles(handle_client_instance)
                file_record = FileRecord(find_file_in_dataset(successor, file_record), handle_client_instance)
                if len(file_record.parents) > 1:
                    unchanged_file = 1
                list_of_files.append(file_record)
                for dset in file_record.parents:
                    output[dset.handle_string] = [successor.errata, file_record.filename, dset.version, order_index, 0, 0, unchanged_file]
            except FileNotFoundInHandle as e:
                incomplete_retracing = 1
                logger.log(e.message)
                break
        # output[dset.handle_string] = [predecessor.errata, dset.id, dset.version, order_index, 0, 1]

    elif aggregation_level == DATASET:
        order_index = 0
        unchanged_file = 0
        dataset_record = DatasetRecord(input_handle, handle_client_instance)
        output[dataset_record.handle_string] = [dataset_record.errata, dataset_record.id, dataset_record.version,
                                                order_index, 0, 0, unchanged_file]
        list_of_datasets = [dataset_record]
        while dataset_record.lineage[0]:
            order_index -= 1
            dataset_record = DatasetRecord(dataset_record.predecessor, handle_client_instance, successor=dataset_record)
            output[dataset_record.handle_string] = [dataset_record.errata, dataset_record.id, dataset_record.version,
                                                    order_index, 0, 0, unchanged_file]
        # Marking entry as First
        dataset_record = list_of_datasets[0]
        order_index = 0
        while dataset_record.lineage[1]:
            order_index += 1
            dataset_record = DatasetRecord(dataset_record.successor, handle_client_instance, predecessor=dataset_record)
            output[dataset_record.handle_string] = [dataset_record.errata, dataset_record.id, dataset_record.version,
                                                    order_index, 0, 0, unchanged_file]
        # Marking entry as Latest
    else:
        raise UnresolvedAggregationLevel

    return output, incomplete_retracing

