# def flatten(current, result=[]):
#     if isinstance(current, dict):
#         for key in current:
#             flatten(current[key], result)
#     else:
#         result.append(current)
#     return result

import ndmg



def test_flatten():
    current = {'adjacency': '/mnt/d/Downloads/ne...adjacency',
               'base': '/mnt/d/Downloads/ne...utputs/qa',
               'fibers': '/mnt/d/Downloads/ne...qa/fibers',
               'graphs': '/mnt/d/Downloads/ne...qa/graphs',
               'graphs_plotting': '/mnt/d/Downloads/ne..._plotting',
               'mri': '/mnt/d/Downloads/ne...ts/qa/mri',
               'reg': '/mnt/d/Downloads/ne...ts/qa/reg',
               'tensor': '/mnt/d/Downloads/ne...qa/tensor'}
    value = ndmg.utils.bids_utils.flatten(current, [])
    print(value)
    assert value ==     ['/mnt/d/Downloads/ne...adjacency',
                         '/mnt/d/Downloads/ne...utputs/qa',
                         '/mnt/d/Downloads/ne...qa/fibers',
                         '/mnt/d/Downloads/ne...qa/graphs',
                         '/mnt/d/Downloads/ne..._plotting',
                         '/mnt/d/Downloads/ne...ts/qa/mri',
                         '/mnt/d/Downloads/ne...ts/qa/reg',
                         '/mnt/d/Downloads/ne...qa/tensor']

test_flatten()