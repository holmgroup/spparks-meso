# -*- coding: utf-8 -*-
"""
    meso.nxjson
    ~~~~~~~~~~~

    This module provides json serialization for use with Karsten Borgwardt's matlab code

    :copyright: (c) 2015 by Brian DeCost
    :license: MIT, see LICENSE for more details.
"""

#   issue: not sure arbitrary integer keys are going to work.
#    KB's example datasets are contiguous 1--N float64s

import json
import numpy as np
import networkx as nx
# import matlab.engine

# print('starting matlab...')
# mlab = matlab.engine.start_matlab()
# print('matlab loaded.')


def adjacency_matrix(graph):
    """ am is a list of adjacency matrices.
        nx -> numpy -> list of lists """
    am = nx.to_numpy_matrix(graph)
    am = np.asarray(am)
    # json needs python int, not np.int
    return list(list(map(float, row)) for row in am)


def adjacency_list(graph):
    """ al is a list of adjacency lists
        element i: list of adjacent nodes for node i"""
    return [[float(edge) for edge in graph[node]]for node in graph]


def node_labels(graph, label_key=None):
    """ nl is a list of dictionaries containing node labels
        each dict key corresponds to a node attribute
        Borgwardt code expects values to be a column vector of doubles
        write as a single list here and transpose in MATLAB
        these keys map to a list of doubles, one per node
    """
    def _label(node_data):
        try:
            return node_data[label_key]
        except KeyError:
            return 1.0

    return {'values': list(_label(data) for __, data in graph.nodes(data=True))}


def graph_labels(graphs):
    ''' return column vector of labels '''
    labels = list(float(1) for g in graphs)
    return labels


def convert_graph(graph):
    """ Borgwardt's code uses consecutive integers starting at 1
          for node labels (represented as float64).
          Preserve ordering of nodes in graph """
    return nx.convert_node_labels_to_integers(graph, first_label=1)


def nx_to_borgwardt(graphs, label_key=None, name='data',):
    ''' convert a list of networkx graphs to Borgwardt's MATLAB format.
        am: adjacency matrix
        al: adjacency list
        nl.values: column vector of node labels
        el: contains edge labels (optional, excluding for now)
        parameter name='data': don't change this without changing nxjson.m
    '''
    converted = [convert_graph(graph) for graph in graphs]

    dataset = [{'nl': node_labels(g, label_key=label_key),
                'al': adjacency_list(g),
                'am': adjacency_matrix(g)} for g in converted]

    labels = graph_labels(converted)

    return {'data': dataset, 'labels': labels}


def graphlist_to_json(graphs, path='test.json', node_label_key=None):
    """ serialize a list of networkx graphs into a json format
          that can be parsed by MATLAB using nxjson.m into the
          format used by Bordwardt's graph kernel code
    """
    data = nx_to_borgwardt(graphs, label_key=node_label_key)

    with open(path, 'w') as jf:
        # json.dump(data, jf, indent=2)
        print(json.dumps(data), file=jf)
    return


####################
# helper functions #
####################
def random_graphs(n_graphs=10):
    g = [nx.gnp_random_graph(5, 0.8) for i in range(n_graphs)]
    return g


def star_graphs(n_graphs=10):
    g = [nx.star_graph(i) for i in range(3, n_graphs + 3)]
    return g


def atlas():
    from networkx.generators.atlas import graph_atlas_g
    graphs = graph_atlas_g()
    graphs = [g for g in graphs if (g.size() > 5 and nx.is_connected(g))]
    return graphs


def test_dataset():
    print('writing test graph dataset to ./test.json')
    graphs = star_graphs(n_graphs=3)
    graphlist_to_json(graphs, path='test.json')

if __name__ == '__main__':
    test_dataset()
