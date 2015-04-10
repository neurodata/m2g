%code snippet to find centroids
%questions to willgray@jhu.edu

%centroids are floats - users may wish to round these values
%so that they fall squarely on a voxel

labels = ReadXml('MNI152_T1_1mm_brain_labels.xml');
% Optional, but recommended - trim these with brain mask
% to avoid using dilated labels
mask = ReadXml('MNI152_T1_1mm_brain_mask.xml');
labels(mask == 0) = 0;


%use original label space, 1-indexed
for i = 1:135
    idx = find(labels == i);
    
    %unexpected behavior when doing this directly, so using ind2sub
    %to be more explicit
    [x,y,z] = ind2sub(size(labels),idx);
    centroid(i,:) = [mean(x),mean(y),mean(z)];
end

%trim labels that don't exist, convert to 1-70 convention
centroid = centroid([1:35,101:135],:);

%Optional
%centroid = round(centroid);