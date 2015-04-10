%% Fiber Reader, for use with Camino type images
% Version 0.1,  G. Kiar     04.07.2015 Initial Release

function [fibers, fHeader] = fiberReader_camino(fileName);

fid = fopen(fileName, 'rb');
n = 0;
while ~feof(fid)
    n = n+1;
    len = fread(fid, 1, 'float', 0, 'b');
    fibers(n).length = len;
    fibers(n).resv = ' ';
    fibers(n).rgb = [255;0;0];
    temp = fread(fid, 1, 'float', 0, 'b');
    fibers(n).nSelectFiberStart = temp;
    fibers(n).nSelectFiberEnd = temp+len;
    if ~mod(n, 10000)
        fprintf('Processing fiber number: %d\n', n);
    end
    for i=1:len
        xyz(1) = fread(fid, 1, 'float', 0, 'b');
        xyz(2) = fread(fid, 1, 'float', 0, 'b');
        xyz(3) = fread(fid, 1, 'float', 0, 'b');
        fibers(n).xyzdat(i,:) = xyz;
    end
end
fibers(n) = [];

fHeader.sFiberFileTag = 'FiberDat';
fHeader.nFiberNr = size(fibers,2);
fHeader.nReserved = -1;
fHeader.fReserved = -1;
fHeader.nImgWidth = -1;
fHeader.nImgHeight = -1;
fHeader.nImgSlices = -1;
fHeader.fPixelSizeWidth = -1;
fHeader.fPixelSizeHeight = -1;
fHeader.fSliceThickness = -1;
fHeader.cSliceOrientation = -1;
fHeader.cSliceSequencing = -1;

end