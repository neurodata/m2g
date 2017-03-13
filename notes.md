## notes from @gkiar running/testing+inspecting/integrating the fmri-merge branch of ndmg

### running
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
| installation | :heavy_check_mark: | :heavy_check_mark: | no obvious problems |
| dwi demo (`ndmg_demo-dwi`) | :heavy_check_mark: | :heavy_check_mark: | same behaviour as master |
| func demo (`ndmg_demo-func`) | :x: | :heavy_check_mark: | **(1)** does not run - it appears that you are not passing parameters properly to the pipeline; **(2)** the demo downloads atlases ranging from 1mm-4mm in resolution, which is unnecessary. demo should do bare minimum (i.e. download only the atlases used in the demo); **(3)** demo data should be downloaded from s3 not brainstore, to reduce chance of outages; **(4)** there should be 1 file downloaded for each demo, eventually 1 total, but there were 2 or 3? ***all are now fixed***|
| func pipeline (`fngs_pipeline`) | :heavy_check_mark: | :heavy_check_mark: | ran on demo data once the demo was fixed. |
| func pipeline (`fngs_pipeline`) | :hourglass: | :hourglass: | have not yet run on abritrary full-sized dataset. |


### testing+inspecting
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
|    |    |    |   |


### integrating
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
| demos | :x: | :x: | **(1)** should be 1 demo that generates multi-connectomes; **(2)** they should use the same subject/session for both dwi and fmri; **(3)** for the sake of consistency, input files should be organized in BIDS |
| func pipeline (`fngs_pipeline`) | :x: | :x: | **(1)** needs to be renamed `ndmg_pipeline` and accept flag for functional or diffusion; **(2)** should do QC along the way, as derivatives are produced, not just at the end; |
