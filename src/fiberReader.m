%% Fiber Reader, for use with MRI Studio type images
% See www.mristudio.org/wiki/faq for more information
% Version 0.1,  W. Gray     12.01.2010 Initial Release
% Version 0.2,  J. Bogovic  12.02.2010 Updates and bug fixes
% Version 0.25,  W. Gray      09.12.2012 - removed inner for loop - 5-10x
% speed up expected in read time

function [fibers, fHeader] =  fiberReaderDist(fileName) %#ok<FNDEF>

fileName %#ok<NOPRT>

fid = fopen(fileName,'rb');

fHeader.sFiberFileTag = fread(fid,8,'*char');
fHeader.sFiberFileTag;
fHeader.sFiberFileTag = fHeader.sFiberFileTag';
fHeader.nFiberNr = fread(fid,1,'int');
fHeader.nReserved = fread(fid,1,'int');
fHeader.fReserved = fread(fid,1,'float');
fHeader.nImgWidth = fread(fid,1,'int');
fHeader.nImgHeight = fread(fid,1,'int');
fHeader.nImgSlices = fread(fid,1,'int');
fHeader.fPixelSizeWidth = fread(fid,1,'float');
fHeader.fPixelSizeHeight = fread(fid,1,'float');
fHeader.fSliceThickness = fread(fid,1,'float');

%Storing next 2 as numbers, rather than Chars
fHeader.cSliceOrientation = fread(fid,1);%'1*char');%,'*char');
fHeader.cSliceSequencing = fread(fid,1);%'1*char');%'*char');

%Skip to 128
fseek(fid,128,'bof');

fibers = struct([]);
fHeader.nFiberNr



% Read the fiber data
for i = 1:fHeader.nFiberNr
% for i = 1:20

    
    if mod(i,10000) == 0
        fprintf('Number of fibers processed: %d\n',i);
    end
    
    fibers(i).length = fread(fid,1,'int');
    fibers(i).resv = fread(fid,1,'*char');
    % fibers(i).rgb = fread(fid,[3,1],'int');
    
    rgb =  zeros(3,1);
    %
    rgb(1) = fread(fid,1,'*char');
    rgb(2) = fread(fid,1,'*char');
    rgb(3) = fread(fid,1,'*char');
    fibers(i).rgb = rgb;
    
    fibers(i).nSelectFiberStart = fread(fid,1,'int');
    fibers(i).nSelectFiberEnd = fread(fid,1,'int');
    
    %
    %         xyzdat = zeros(fibers(i).length,3);
    %                  for j = 1:size(xyzdat,1)
    %             xyzdatold(j,1) = fread(fid,1,'float');
    %              xyzdatold(j,2) = fread(fid,1,'float');
    %              xyzdatold(j,3) = fread(fid,1,'float');
    %          end
    
    xyzdat = fread(fid,[3,fibers(i).length],'float');
    fibers(i).xyzdat = xyzdat';
    
end

fclose(fid);