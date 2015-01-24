function data = openRawFile2(filename,volumeDim,dType)
    %OPENRAWFILE Summary of this function goes here
    %   Detailed explanation goes here

    if strcmpi(dType,'Float') == 1                
        dType = 'float32';
    elseif strcmpi(dType,'Short') == 1  
        dType = 'short';
    end

    fid = fopen(filename);
    data = reshape(fread(fid, prod(volumeDim), dType, 0, 'b'),volumeDim);
    fclose(fid);
end

