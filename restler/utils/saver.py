# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

""" Saver module. """
import os
import pickle

import utils.logger as logger
import utils.formatting as formatting


def save(req_collection, seq_collection, fuzzing_collection, fuzzing_monitor, length):
    """ Save in checkpoint fuzzing of latest generation.

    @param req_collection: The request collection.
    @type  req_collection: RequestCollection class object.
    @param seq_collection: List of sequences in sequence collection.
    @type  seq_collection: List
    @param fuzzing_collection: The collection of requests being fuzzed
    @type  fuzzing_collection: FuzzingRequestCollection
    @param fuzzing_monitor: The global monitor for the fuzzing run
    @type  fuzzing_monitor: FuzzingMonitor
    @param length: Length of latest generation.
    @type length: Int

    @return: None
    @rtype : None

    """
    return


def load(req_collection, seq_collection, fuzzing_collection, fuzzing_monitor):
    """ Load from checkpoint fuzzing of lattest generation.

    @param req_collection: The target request collection.
    @type  req_collection: RequestCollection class object.
    @param seq_collection: The tareg list of sequences in sequence collection.
    @type  seq_collection: List
    @param length: Length of lattest generation.
    @type length: Int

    @return: A tuple of ('length', request collection', 'sequence collection')
    @rtype : Tuple

    """
    length = 0
    print("No checkpoints used at this phase")
    return req_collection, seq_collection, fuzzing_collection, fuzzing_monitor, length
