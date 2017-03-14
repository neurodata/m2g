## notes from @gkiar running/testing+inspecting/integrating the fmri-merge branch of ndmg

### running
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
| installation | :heavy_check_mark: | :heavy_check_mark: | no obvious problems |
| dwi demo (`ndmg_demo-dwi`) | :heavy_check_mark: | :heavy_check_mark: | same behaviour as master |
| func demo (`ndmg_demo-func`) | :x: | :heavy_check_mark: | **(1)** does not run - it appears that you are not passing parameters properly to the pipeline; **(2)** the demo downloads atlases ranging from 1mm-4mm in resolution, which is unnecessary. demo should do bare minimum (i.e. download only the atlases used in the demo); **(3)** demo data should be downloaded from s3 not brainstore, to reduce chance of outages; **(4)** there should be 1 file downloaded for each demo, eventually 1 total, but there were 2 or 3? ***all are now fixed***|
| func pipeline (`fngs_pipeline`) | :heavy_check_mark: | :heavy_check_mark: | ran on demo data once the demo was fixed. |
| func pipeline (`fngs_pipeline`) | :hourglass: | :hourglass: | have not yet run on abritrary full-sized dataset. |
| bids pipeline (`ndmg_bids`) | :x: | :heavy_check_mark: | **(1)** should not default to doing neither dwi or func analysis, should be a "choice" input like analysis level (eventually this will be irrelevant as they will be one in the same, but currently is bad); **(2)** currently the `participant_level_func` module is a verbatim copy of the dwi equivalent, with minor changes - meaning, we should only have 1 of these functions; **(3)** logic was convoluted (my own fault) for getting subject lists, etc., so needs to be cleaned and modularized. ***All of these are now done***|


### testing+inspecting
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
| performance | :hourglass: | :hourglass: | have not run discriminability |
| registration | :hourglass: | :hourglass: | **(1)** we are currently not resampling after registration, though we do it for qc figs. We should test the pipeline with this resampling happening directly after reg and re-evaluate performance; **(2)** we are skull stripping fmri, which I think we should not do, so we should figure out which is right;|
| graphs| :hourglass: | :hourglass: | have not verified correspondance between nodes in both dwi and fmri graphs |



### integrating
| Topic | Initial Status | Current Status | Notes |
|:------|:---------------|:---------------|:------|
| demos | :x: | :x: | **(1)** should be 1 demo that generates multi-connectomes; **(2)** they should use the same subject/session for both dwi and fmri; **(3)** for the sake of consistency, input files should be organized in BIDS |
| func pipeline (`fngs_pipeline`) | :x: | :x: | **(1)** needs to be renamed `ndmg_pipeline` and accept flag for functional or diffusion; **(2)** should do QC along the way, as derivatives are produced, not just at the end; |
| parcellations | :x: | :x: | **(1)** need either parcellations at both resolutions to make the multigraphs or to process them at the same resolution as one another; |
