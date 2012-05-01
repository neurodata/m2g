
################################################################################
#
#  module: zindex.py
#
#  Routines to convert to/from Morton-order z-index
#
################################################################################

################################################################################
# Name:  XYZtoMorton3D
# Action:  Generate morton order from XYZ coordinates
################################################################################
def XYZMorton ( xyz ):
 
  cdef int x
  cdef int y
  cdef int z

  x, y, z = xyz

  cdef int morton = 0
  cdef int mask = 0x001

  #21 triads of 3 bits each 
  cdef int i
  for  i in range(21):
  
    # This logic is a little confusing. 
    # Perform the shifts relative to their position 
    # this allows us just to shift the mask and not each value 

    # Extract the low bits and assign 
    morton += (x & mask) << (2*i)
    morton += (y & mask) << (2*i+1)
    morton += (z & mask) << (2*i+2)
    
    # Shift maske  by one bit 
    mask <<= 1
   
  return morton

################################################################################
# Name: generator
# Action: iterate in mortonorder for the specified range
################################################################################

def generator ( dim ):

  # This is a little wasteful of computation
  cdef int i=0
  cdef int x
  cdef int y
  cdef int z

  while True:
    [x,y,z] = MortonXYZ ( i )
    if x < dim[0] and y < dim[1] and z < dim[2]:
      yield i
    elif x >= dim[0] and y >= dim[1] and z >= dim[2]:
      return
    i = i+1


################################################################################
# Name:  Morton3DtoXYZ
# Action:  Generate XYZ coordinates from Morton index
################################################################################

def MortonXYZ (int morton):

  cdef int xmask = 0x001
  cdef int ymask = 0x002
  cdef int zmask = 0x004

  cdef int xp = 0x00
  cdef int yp = 0x00
  cdef int zp = 0x00

  cdef int i

  # 21 triads of 3 bits each 
  for i in range(21):

    xp += (xmask & morton) << i 
    yp += ((ymask & morton) << i ) >> 1 
    zp += ((zmask & morton) << i) >> 2 
    morton >>= 3;

  return [ xp, yp, zp ]


