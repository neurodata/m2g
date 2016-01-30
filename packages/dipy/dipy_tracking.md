## Dipy Tracking Methods

In Dipy, there seem to be several different approaches to deterministic and probabilistic tracking.

Recommended starting point:

- [Option 1](https://github.com/nipy/dipy/blob/master/doc/examples/introduction_to_basic_tracking.py)

- these methods aren't obviously from papers, but seem reasonable.  The deterministic version basically is the probabilistic version that always chooses the peak of the distribution.

- EuDX is a "fact like" method that does have a paper and dissertation behind it.  This is what we built as a first pass - 

- [Tensor version](https://github.com/nipy/dipy/blob/master/doc/examples/tracking_eudx_tensor.py). You'll first need to run the tensor tracking [here](https://github.com/nipy/dipy/blob/master/doc/examples/reconst_dti.py)

- [ODF version](https://github.com/nipy/dipy/blob/master/doc/examples/tracking_eudx_odf.py)

Next steps are to reread the dipy paper and see if we can get some traction on recommended methods.

