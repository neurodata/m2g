import numpy as np
import ndmg

np.set_printoptions(threshold=np.inf)


# def get_sphere(coords, r, vox_dims, dims):
#     r = float(r)
#     xx, yy, zz = [
#         slice(-r / vox_dims[i], r / vox_dims[i] + 0.01, 1) for i in range(len(coords))
#     ]
#     cube = np.vstack([row.ravel() for row in np.mgrid[xx, yy, zz]])
#     sphere = cube[:, np.sum(np.dot(np.diag(vox_dims), cube) ** 2, 0) ** 0.5 <= r]
#     sphere = np.round(sphere.T + coords)
#     neighbors = sphere[
#                 (np.min(sphere, 1) >= 0) & (np.max(np.subtract(sphere, dims), 1) <= -1), :
#                 ].astype(int)
#     return neighbors


def test_get_sphere():
    a = (10, 20, 30)
    r = 80
    c = (40, 50, 60)
    d = (70, 80, 90)

    value = ndmg.graph.gen_graph.get_sphere(a, r, c, d)

    test = [[ 9, 19, 30],
            [ 9, 19, 31],
            [ 9, 20, 30],
            [ 9, 20, 31],
            [10, 19, 30],
            [10, 19, 31],
            [10, 20, 30],
            [10, 20, 31],
            [10, 21, 30],
            [11, 19, 30],
            [11, 19, 31],
            [11, 20, 30],
            [11, 20, 31]]
    assert np.all(value == test)