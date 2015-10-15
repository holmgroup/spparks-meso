import numpy as np
from skimage.segmentation import mark_boundaries

def unit_quat(q):
  q = np.array(q, dtype=np.float32)
  return q / np.linalg.norm(q)


orientation = {'candidate': unit_quat([1,0,0,0]),
               'blue': unit_quat([2,1,0,0]),
               'red': unit_quat([1,1,1,0])}


def random_binary_texture(grains, candidates=[1], red_probability=0.0):
  """ binary texture components that work with cutoff angle of 50 degrees """
  max_grain = np.max(grains)
  quats = np.zeros((max_grain+1, 4))
  for i in range(1, max_grain+1):
    grain_type = 'red' if np.random.rand() < red_probability else 'blue'
    quats[i,:] = orientation[grain_type]
    
  for c in candidates:
    quats[c,:] = orientation['candidate']
    
  return quats


def list_binary_texture(grains, candidates=[1], blues=[]):
  """ assign binary texture -- list of blue grains """
  max_grain = np.max(grains)
  quats = np.zeros((max_grain+1, 4))
  for i in range(1, max_grain+1):
    quats[i,:] = orientation['red']
  for c in candidates:
    quats[c,:] = orientation['candidate']
  for b in blues:
    quats[b,:] = orientation['blue']
  return quats


def colors(grains, quats, boundaries=True):
  color_map = {1: np.array([1.0, 1.0, 1.0]),
               2: np.array([.45, .57, 0.63]),
               3: np.array([0.6, 0.0, 0.0])}

  shape = list(grains.shape) + [3]
  colors = np.zeros(shape)
  for i in range(1, quats.shape[0]):
    colors[grains == i] = color_map[np.sum(quats[i,:] > 0)]
  if boundaries:
    colors = mark_boundaries(colors, grains, color=[0,0,0])

  return colors
