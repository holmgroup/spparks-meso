import numpy as np
import networkx as nx
from scipy import ndimage


def _add_edge_filter(values, graph):
    """ create an edge in graph between first element in values and rest
    see skimage.future.graph
    return 0 for scipy.ndimage.generic_filter
    """
    values = values.astype(int)
    current = values[0]
    for value in values[1:]:
        if value != current:
            graph.add_edge(current, value)
    return 0


def transgranular_network(labels, mode='wrap', connectivity=1):
    """ a lightly modified skimage.future.graph.rag_mean_color 
        modified to allow periodic images
    """
    graph = nx.Graph()

    fp = ndimage.generate_binary_structure(labels.ndim, connectivity)
    for d in range(fp.ndim):
        fp.swapaxes(0, d)
        fp[0, ...] = 0
        fp = fp.swapaxes(0, d)

    ndimage.generic_filter(
        labels,
        function=_add_edge_filter,
        footprint=fp,
        mode=mode,
        output=np.zeros(labels.shape, dtype=np.uint8),
        extra_arguments=(graph,))

    return graph


def add_orientations(graph, quaternions):
    for node, data in graph.nodes(data=True):
        data['orientation'] = quaternions[node]
    return


def neighborhood_graph(graph, root_node, radius=None):
    nbrhd = nx.ego_graph(graph, root_node, radius=radius)
    for node, data in nbrhd.nodes(data=True):
        # follow candidate grain in binary texture scheme
        data['label'] = float(np.sum(data['orientation'] != 0))

    return nbrhd
