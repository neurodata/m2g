```{python}
import os
import os.path as op
import glob
from pathlib2 import Path
from ndmg.scripts import ndmg_dwi_pipeline
from ndmg.utils import s3_utils

# Download test data
data_dir = op.expanduser("~") + "/.ndmg/HNU1t"
if not op.isdir(data_dir):
    os.mkdirs(data_dir)
    s3_utils.s3_get_data('ndmg-data', 'HNU1t', data_dir)

```{python}

# Run ndmg with docker from the command-line
```{bash}
input_dir = $HOME/.ndmg/HNU1t
mkdir $HOME/.ndmg/output

# Option A (Docker executable approach):
docker run -ti --rm --privileged -e DISPLAY=$DISPLAY -v $HOME/.ndmg/HNU1t:/input -v $HOME/.ndmg/output:/outputs ndmg_dev:latest --participant_label 0025427 --session_label 1 --modality dwi --atlas desikan --mod det --tt local --mf csd --sp native /input /output participant

ndmg_bids --bucket ndmg-data --remote_path HNU1t --participant_label 0025427 --session_label 1 --modality dwi --atlas desikan --mod det --tt local --mf csd --sp native /input /output participant

# Option B (Inside Docker container):
docker run -ti --rm --privileged --entrypoint /bin/bash -e DISPLAY=$DISPLAY -v $HOME/.ndmg/HNU1t:/data -v $HOME/.ndmg/output:/outputs ndmg_dev:latest

ndmg_bids --participant_label 0025427 --session_label 1 --modality dwi --atlas desikan --mod det --tt local --mf csd --sp native /input /output participant

# Option C (Docker via NeuroData AWS -- credentials required):
ndmg_bids --bucket ndmg-data --remote_path HNU1t --participant_label 0025427 --session_label 1 --modality dwi --atlas desikan --mod det --tt local --mf csd --sp native /input /output participant
```
