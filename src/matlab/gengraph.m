function graph = gengraph (fiberfile, atlasfile, outfile)
% To generate a connectivity matrix, do the following:
% Version 0.1, W. Gray 02.14.2012
% Version 0.2, G. Kiar 01.07.2014

%% Load data - some hardcoding in this prototype
% addpath /cis/project/migraine/centos6/MR-connectome/M2G/src
% addpath /cis/project/migraine/centos6/NIfTI_20140122

% load fibers
tic
[fiber, header] = fiberReader(fiberfile);
t = toc/60

% load ROIs
nn = load_nii(atlasfile);
% [roiLabel, header] = ReadXml('M87102217_roi.xml');
roiLabel = nn.img;
% manipulate ROIs by subtracting 65 from values greater than 101, and
% masking ROI volume with binary mask extent.
roiLabel(roiLabel > 100) = roiLabel(roiLabel > 100) - 65;

roiLabelMask = roiLabel;

%The following line should be uncommented to generate connectivity masked
%with the brain extent.  Small difference, in practice

%roiLabelMask(binMask == 0) = 0;

%% Compute matrix

fbrCountMtx = zeros(70,70);

% Go through each fiber.  Get an {x,y,z} tuple, and floor coordinates. Flooring is required for
% compliance with FACT algorithm.  For each set of coordinates along a fiber, get ROI value for all points.
% Find unique ROIs for each fiber, and sort result.

% For each pair of ROIs, increment value in 70x70 matrix by 1.

for i = 1:length(fiber) %loop over number of fibers
    
    if mod(i,1000) == 0
        fprintf('Number of fibers processed for connMtx is: %d\n',i);
    end
    
    clear roiAll
    roiAll = [];
    %some fibers have zero length - skip these
    if fiber(i).length > 1 && size(fiber(i).xyzdat,1) > 0
        
        for j = 1:fiber(i).length
            
            idx = fiber(i).xyzdat(j,:);
            idx = ceil(idx)+1;  %this is the convention of FACT
            
            if sum(idx) > 0  && idx(1) <= size(roiLabelMask,1) && idx(2) <= size(roiLabelMask,2) ...
                    && idx(3) <= size(roiLabelMask,3)%necessary to prevent out of bound errors
                roiLookup = roiLabelMask(idx(1),idx(2),idx(3));
                roiAll = [roiAll, roiLookup];
            end
        end
        
        roiAll = unique(roiAll);
        roiAll = sort(roiAll,'ascend');
        
        if ~isempty(roiAll) && roiAll(1) == 0  %disregard 0 labels
            roiAll = roiAll(2:end);
        end
        
        if length(roiAll > 1) % need to have more than one label for a connection to exist
            %now need to increment connMatrix
            
            for m = 1:length(roiAll)
                for n = m+1:length(roiAll)
                    fbrCountMtx(roiAll(m),roiAll(n)) = fbrCountMtx(roiAll(m),roiAll(n))+1;
                end
            end
        end
    end
end

figure, imagesc(log10(fbrCountMtx))
edges = sparse(fbCountMtx)
graph = fbrCountMtx;
save(outfile, fbrCountMtx, edges)
