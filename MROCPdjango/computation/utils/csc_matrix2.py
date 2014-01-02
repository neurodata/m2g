#!/usr/bin/python

# csc_matrix2.py
# Created by Disa Mhembere on 2014-01-02.
# Email: disa@jhu.edu
# Copyright (c) 2014. All rights reserved.


from scipy.sparse.csc import csc_matrix

class csc_matrix2(csc_matrix):
  """
  A class to permit the use of the len func on scipy sparse matrices if they are
  square
  """

  def __len__(self):
    if self.shape[0] != self.shape[1]:
      super(csc_matrix2, self).__len__()
    return self.shape[0]

def test():
  g = csc_matrix2([
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0]
        ])

  print "Using len() the dimension of this matrix is %d" % len(g)

if __name__ == "__main__":
  test()