%% Fiber Writer, for use with MRI Studio type images
% See www.mristudio.org/wiki/faq for more information
% Adapted from Fiber Writer which was created by W. Gray and J. Bogovic
% Version 0.1,  G. Kiar     11.07.2014 Initial Release

function fiberWriter(fileName, fibers, fHeader)

fileName

fid = fopen(fileName,'wb');

fwrite(fid, fHeader.sFiberFileTag, '*char');
fwrite(fid, fHeader.nFiberNr, 'int');
fwrite(fid, fHeader.nReserved, 'int');
fwrite(fid, fHeader.fReserved, 'float');
fwrite(fid, fHeader.nImgWidth,'int');
fwrite(fid, fHeader.nImgHeight, 'int');
fwrite(fid, fHeader.nImgSlices, 'int');
fwrite(fid, fHeader.fPixelSizeWidth, 'float');
fwrite(fid, fHeader.fPixelSizeHeight, 'float');
fwrite(fid, fHeader.fSliceThickness, 'float');
fwrite(fid, fHeader.cSliceOrientation);
fwrite(fid, fHeader.cSliceSequencing);

pos = ftell(fid);
for i=pos:4:128;
    fwrite(fid, -1, 'int');
end
%Skip to 128
fseek(fid,128,'bof');

fHeader.nFiberNr

% Write the fiber data
for i = 1:fHeader.nFiberNr
    
    if mod(i,10000) == 0
        fprintf('Number of fibers processed: %d\n',i);
    end
    fwrite(fid, fibers(i).length, 'int');
    fwrite(fid, fibers(i).resv, '*char');

    fwrite(fid, fibers(i).rgb, '*char');
    
    fwrite(fid, fibers(i).nSelectFiberStart, 'int');
    fwrite(fid, fibers(i).nSelectFiberEnd, 'int');

    fwrite(fid, fibers(i).xyzdat', 'float');

end
fclose(fid);

end