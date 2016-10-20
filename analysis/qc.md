Standard = the reference result to which we are comparing the pipeline to

## Image QC

Error = | Standard Volume - Aligned Volume |

## Tensor QC

Error = | Standard Tensor Image - Tensor Image |

## Fiber QC

Error =  sum of | Standard fiber points - fiber points | for every voxel which has a fiber seeded there

## Graph QC

Error = | Standard Adj - Adj matrix |
