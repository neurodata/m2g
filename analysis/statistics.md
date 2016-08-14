### Image Metrics
| Metric         | Description                            | Derivative Evaluated | Relevant Modalities        |
|----------------|----------------------------------------|----------------------|----------------------------|
| overlap        | between produced image and target      | aligned volume       | T1w/MPRAGE, DTI, fMRI      |
| jitter         | between produced image and target      | aligned volume       | T1w/MPRAGE, DTI, fMRI      |
| kde + distance | between produced image and target      | aligned volume       | T1w/MPRAGE, DTI, fMRI      |
| voxelwise mean | of image                               | aligned 4D volume    | DTI (FA), fMRI (intensity) |
| voxelwise std  | of image                               | aligned 4D volume    | DTI (FA), fMRI (intensity) |
| voxelwise snr  | of image                               | aligned 4D volume    | DTI (FA), fMRI (intensity) |


### Graph Metrics
| Metric                    | Description                            | Derivative Evaluated | Relevant Modalities        |
|---------------------------|----------------------------------------|----------------------|----------------------------|
| Number of non-zero edges  | count of binary edges                  | graph                | DTI, fMRI (if thresholded) |
| Degree                    | of each node in the graph              | graph                | DTI, fMRI (if thresholded) |
| Edge weight               | of each edge in the graph              | graph                | DTI, fMRI                  |
| Clustering coefficient    | of each node in the graph              | graph                | DTI, fMRI                  |
| Scan statistic-1          | of each node in the graph              | graph                | DTI, fMRI (if thresholded) |
| Betweenness centrality    | of each node in the graph              | graph                | DTI, fMRI (if thresholded) |
| Eigen values              | of graph laplacian                     | graph                | DTI, fMRI                  |
| Scree plot                | of graph variance                      | graph                | DTI, fMRI                  |
