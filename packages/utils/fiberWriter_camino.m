%% Fiber Writer, for use with MRI Studio type images
% Version 0.1,  G. Kiar     04.07.2014 Initial Release

function fiberWriter_camino(fileName, fibers, fHeader)

fileName

fid = fopen(fileName,'wb');
fHeader.nFiberNr

for i=1:fHeader.nFiberNr
    if mod(i,10000) == 0
        fprintf('Number of fibers processed: %d\n',i);
    end
    fwrite(fid, fibers(i).length, 'float', 0, 'b');
    fwrite(fid, fibers(i).nSelectFiberStart, 'float', 0, 'b');
    fwrite(fid, fibers(i).xyzdat', 'float', 0, 'b');
end
fclose(fid);

end