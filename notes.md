## notes from @gkiar running/testing+inspecting/integrating the fmri-merge branch of ndmg

### running
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
| installation | :heavy_check_mark: | :heavy_check_mark: | no obvious problems |
| dwi demo (`ndmg_demo-dwi`) | :heavy_check_mark: | :heavy_check_mark: | same behaviour as master |
| func demo (`ndmg_demo-func`) | :x: | :x: | **(1)** produces error as what appear to be duplicates files being downloaded are overwriting each other; **(2)** the demo downloads atlases ranging from 1mm-4mm in resolution, which is unnecessary. demo should do bare minimum (i.e. download only the atlases used in the demo). **(3)** demo data should be downloaded from s3 not brainstore, to reduce chance of outages. **(4)** there should be file downloaded for all demos, there were 3?|
| func pipeline (`fngs_pipeline`) | :x: | :x: | **(1)** needs to be renamed `ndmg_pipeline` and accept flag for functional or diffusion |


### testing+inspecting
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
|    |    |    |   |


### integrating
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
|    |    |    |   |
