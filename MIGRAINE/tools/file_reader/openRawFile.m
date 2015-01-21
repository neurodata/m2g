function data = openRawFile(filename, volumeDim)
    %OPENRAWFILE Summary of this function goes here
    %   Detailed explanation goes here
    
    fid = fopen(filename);
    data = reshape(fread(fid, prod(volumeDim), 'single=>single', 0, 'b'),volumeDim);
    fclose(fid);
end

