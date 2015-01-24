function [image, header] = mhdread(filepath)
% MHDREAD Reads a MetaImage (.mhd) file.
%   IMAGE = MHDREAD(FILEPATH), where FILEPATH is the absolute or relative
%   path to the header (.mhd) file, and returns the IMAGE volume.
%
%   [IMAGE, HEADER] = MHDREAD(FILEPATH) optionally returns the parsed
%   HEADER as a struct with tags corresponding to each line of the header.
%
% Please refer to http://www.itk.org/Wiki/ITK/MetaIO/Documentation for
% further details on the image file format.

%> @fn mhdread(in filepath)
%> @todo(auneri1) Add support for displacement fields.
%> @todo(auneri1) Handle potential case differences.

% ------------
% Read header
% ------------
assertion = logical(exist(filepath, 'file'));
assert(assertion, 'File not found: %s', filepath);
fid = fopen(filepath, 'rt');

% Create the header struct
header = struct();

tline = fgetl(fid);
while ischar(tline)
    s = find(tline=='=', 1, 'first');
    header.(strtrim(tline(1:s-1))) = strtrim(tline(s+1:end));
    tline = fgetl(fid);
end

% Typecast tag values to expected types
for fieldname = fieldnames(header)'
    tag = char(fieldname);
    switch(tag)
        case 'Comment'
        case 'ObjectType'
        case 'TransformType'
        case 'NDims'
            header.(tag) = str2double(header.(tag));
        case 'Name'
        case 'ID'
            header.(tag) = str2double(header.(tag));
        case 'ParentID'
        case 'CompressedData'
            header.(tag) = strcmpi(header.(tag), 'True');
        case 'CompressedDataSize'
            header.(tag) = str2double(header.(tag));
        case 'BinaryData'
            header.(tag) = strcmpi(header.(tag), 'True');
        case 'BinaryDataByteOrderMSB'
            header.(tag) = strcmpi(header.(tag), 'True');
        case 'ElementByteOrderMSB'
            header.(tag) = strcmpi(header.(tag), 'True');
        case 'Color'
            header.(tag) = str2num(header.(tag)); %#ok<ST2NM>
        case 'Offset'
            header.(tag) = str2num(header.(tag)); %#ok<ST2NM>
        case 'TransformMatrix'
            header.(tag) = reshape(str2num(header.(tag)), header.NDims, header.NDims); %#ok<ST2NM>
        case 'CenterOfRotation'
            header.(tag) = str2num(header.(tag)); %#ok<ST2NM>
        case 'AnatomicalOrientation'
        case 'ElementSpacing'
            header.(tag) = str2num(header.(tag)); %#ok<ST2NM>
        case 'DimSize'
            header.(tag) = str2num(header.(tag)); %#ok<ST2NM>
        case 'HeaderSize'
            header.(tag) = str2num(header.(tag)); %#ok<ST2NM>
        case 'Modality'
        case 'SequenceID'
            header.(tag) = str2double(header.(tag));
        case 'ElementMin'
            header.(tag) = str2double(header.(tag));
        case 'ElementMax'
            header.(tag) = str2double(header.(tag));
        case 'ElementNumberOfChannels'
            header.(tag) = str2double(header.(tag));
        case 'ElementSize'
            header.(tag) = str2num(header.(tag)); %#ok<ST2NM>
        case 'ElementType'
            switch(header.(tag))
                case 'MET_CHAR'
                    header.(tag) = 'int8';
                case 'MET_UCHAR'
                    header.(tag) = 'uint8';
                case 'MET_SHORT'
                    header.(tag) = 'int16';
                case 'MET_USHORT'
                    header.(tag) = 'uint16';
                case 'MET_INT'
                    header.(tag) = 'int32';
                case 'MET_UINT'
                    header.(tag) = 'uint32';
                case 'MET_FLOAT'
                    header.(tag) = 'single';
                case 'MET_DOUBLE'
                    header.(tag) = 'double';
                otherwise
                    warning('MATLAB:UnknownIdentifier', 'Unhandled element type: %s', header.(tag));
            end
        case 'ElementDataFile'
        otherwise
            warning('MATLAB:UnknownIdentifier', 'Unhandled tag: %s', tag);
    end
end
fclose(fid);


% ----------
% Read data
% ----------
[pathstr, ~, ~] = fileparts(filepath);
if isempty(pathstr)
    filepath_data = header.ElementDataFile;
else
    filepath_data = [pathstr filesep header.ElementDataFile];
end
assertion = logical(exist(filepath_data, 'file'));
assert(assertion, 'File not found: %s', filepath_data);
fid = fopen(filepath_data, 'r');

if isfield(header, 'HeaderSize')
    fseek(fid, header.HeaderSize, 'bof');
else
    frewind(fid);
end

if ~isfield(header, 'CompressedData') || ~header.CompressedData
    image = fread(fid, inf, sprintf('*%s', header.ElementType));
else
    image_compressed = fread(fid, inf, 'uchar=>uint8');
    assertion = length(image_compressed) == header.CompressedDataSize;
    assert(assertion, 'Read data size does not match header (CompressedDataSize)');
    image = zlibdecompress(image_compressed, header.ElementType);
end
fclose(fid);

image = reshape(image, header.DimSize);


function uncompressed = zlibdecompress(compressed, element_type)
% ZLIBDECOMPRESS Implements zlib decompression.

import com.mathworks.mlwidgets.io.InterruptibleStreamCopier;
istream = java.io.ByteArrayInputStream(compressed);
ostream = java.io.ByteArrayOutputStream();
inflater = java.util.zip.InflaterInputStream(istream);
copier = InterruptibleStreamCopier.getInterruptibleStreamCopier();
copier.copyStream(inflater, ostream);
inflater.close();
uncompressed = typecast(ostream.toByteArray(), element_type);
