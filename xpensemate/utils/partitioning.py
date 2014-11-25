#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Dana Christen
#
# This file is part of XpenseMate, a tool for managing shared expenses and
# hosted at https://github.com/danac/xpensemate.
#
# XpenseMate is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
This module contains the code used to find subsets of members who can settle
their debts on their own.
"""

from xpensemate.utils import partition_list


def clustering(l, K):
    """
    Returns a generator to all possible k-way partitions of a given list.
    
    Based on `a thread found on StackOverflow
    <http://stackoverflow.com/questions/18353280/iterator-over-all-partitions-into-k-groups>`_.
    
    :param list l: List to a partition whose elements must be comparable
        (i.e. implement the ``__lt__()`` method).
    :param int K: The number of subsets into which the list is to be partitioned.
 
    :return: All possible partitionings.
    :rtype: Generator yielding lists of lists 
    
    Example input:
    
    .. code-block:: python
    
        clustering([0, 1, 2, 3], 2)


    Corresponding output:
    
    .. code-block:: python
    
            [[[0, 1, 2], [3]],
            [[1, 2], [0, 3]],
            [[0, 1, 3], [2]],
            [[1, 3], [0, 2]],
            [[0, 1], [2, 3]],
            [[1], [0, 2, 3]],
            [[0], [1, 2, 3]],
            [[], [0, 1, 2, 3]]]

    """
        
    if len(l) > 0:
        prev = None
        for t in clustering(l[1:], K):
            tup = sorted(t)
            if tup != prev:
                prev = tup
                for i in range(K):
                    yield tup[:i] + [[l[0]] + tup[i],] + tup[i+1:]
    else:
        yield [[] for _ in range(K)]


def non_empty_clustering(l, K):
    """
    Wraps :func:`clustering` while filtering out partitions containing empty
    lists.
    
    :param list l: List to a partition whose elements must be comparable
        (i.e. implement the ``__lt__()`` method).
    :param int K: The number of subsets into which the list is to be partitioned.
 
    :return: The same output as :func:`clustering`, with partitions containing
        empty lists filtered out.
    :rtype: Generator yielding lists of lists
    """
    
    for c in clustering(l, K):
        if all(x for x in c): yield c


def generate_partitions(size):
    """
    Based on a given size :math:`s`, generates a list of all partitions
    returned by :func:`non_empty_clustering` applied to the list of integers
    from 0 to :math:`s`, for all :math:`1<k<s-1`.
    
    Partitions containing singletons are filtered out, which means that
    the output of this function corresponds to that of :func:`clustering`
    module without partitions containing singletons or empty sets.
    
    Partitions are sorted by decreasing values of :math:`k` (i.e. partitions
    with more subsets come first).
    
    :param int size: The set size for which partitions must be generated. 
         
    :return: All possible partitions for the given set size.
    :rtype: Generator yielding lists of lists. 
        Similar to the generators returned by :func:`clustering` and
        :func:`non_empty_clustering` if they were applied to ``range(size)``.
        
    Example output, for size=4:
    
    .. code-block:: python
    
        [[[1, 2, 3], [0, 4]],
         [[0, 1, 4], [2, 3]],
         [[1, 4], [0, 2, 3]],
         [[1, 2, 4], [0, 3]],
         [[0, 1, 3], [2, 4]],
         [[1, 3], [0, 2, 4]],
         [[0, 1, 2], [3, 4]],
         [[1, 2], [0, 3, 4]],
         [[1, 3, 4], [0, 2]],
         [[0, 1], [2, 3, 4]]]    
    
    """    
    permutations = []
    l = range(size)
    for k in range(size//2, 1, -1):
        for i in non_empty_clustering(l,k):
            if len([ ii for ii in i if len(ii) == 1]) == 0:
                yield i


def apply_partitions(l):
    """
    Given a list of elements, returns all partitions of that list based
    on the pastitions in :data:`xpensemate.utils.partition_list.partitions`
    (which are generated by :func:`generate_partitions`). an exception is raised
    if the list of partitions in :data:`xpensemate.utils.partition_list.partitions`
    is not available for the size of the list.
    
    :param list l: The list to partition.
    
    :return: The same output as :func:`generate_partitions`, but applied to the
        given list instead of a list of positive integers.
    :rtype: Generator yielding lists of lists
    :raises: NotImplementedError
    """
    
    try:
        for partition in partition_list.partitions[len(l)]:
            partitioned_list = []
            for subset in partition:
                partitioned_list.append([l[x] for x in subset])
            yield partitioned_list
    except KeyError:
        raise NotImplementedError("Partitioning not implemented for sets of {} elements")


def create_partition_list(file_path = "_partition_list_inline.py", upper_limit = 9, variable_name = "partitions"):
    """
    Generates Python code based on the output of :func:`generate_partitioning`
    that is exec'd in :mod:`xpensemate.utils.partition_list`
    to populate :data:`xpensemate.utils.partition_list.partitions`.
    
    :param str file_path: Path to the file where to save the Python code.
    :param int upper_limit: An upper limit to the size of sets for which partitions are calculated.
    :param str variable_name: Name of the variable used in the Python code, which must export a ``dict``-like interface.
    :return: Nothing
        
    """
    with open(file_path, 'w') as f:
        f.write("{} = dict()\n".format(variable_name))
        for i in range(4, upper_limit+1):
            print("Generating partitions for sets of size {}".format(i))
            src = "{}[{}] = {}\n".format(variable_name, i, repr(list(generate_partitions(i))))
            f.write(src)


def find_zero_balance_subsets(l):
    """
    Given a list of summable items, this finds subsets of the list whose
    elements sum up to zero. This function calls
    :func:`xpensemate.utils.partitioning.apply_partitions`. It returns the argument
    as is if the partitioning is not implemented for the right size.
    
    :param list l: A list of summable elements.
    :return: A list of list describing the partitioning.
    """
    try:
        for i in apply_partitions(l):
            #print("--Checking {}".format(len(i)))
            flag = True
            for j in i:
                flag = flag and is_null(sum(j))
            if flag:
                return parts
    except NotImplementedError:
        return l,
    return l,
