function header_out = mhdwrite(image, filepath, header_in)
% MHDWRITE Writes a MetaImage (.mhd) file.
%   HEADER_OUT = MHDWRITE(IMAGE, FILEPATH) writes the input IMAGE volume to
%   the absolute or relative FILEPATH of the header file. Image dimensions
%   and element data type are inferred from the image, and all other tags
%   in the header use default values. HEADER_OUT struct used is returned.
%
%   HEADER_OUT = MHDWRITE(IMAGE, FILEPATH, HEADER_IN) optionally input a
%   HEADER_IN struct which can contain some or all of the header
%   information.
%
%   HEADER_OUT = MHDWRITE() returns a HEADER_OUT struct with all available
%   tags set to NaN.
%
% Please refer to http://www.itk.org/Wiki/ITK/MetaIO/Documentation for
% further details on the image file format.

%> @fn mhdwrite(in image, in filepath, in header_in)
%> @todo(auneri1) Add support for displacement fields.
%> @todo(auneri1) Consider using inputParser instead.
%> @todo(auneri1) Convert ElementDataFile extension to zraw if raw.
%> @todo(auneri1) Add support for typecasting.

if nargin < 3
    header_in = struct();
end

% Populate the header struct
header = struct();
for fieldname = { ...
        'Comment', ...
        'ObjectType', ...
        'TransformType', ...
        'NDims', ...
        'Name', ...
        'ID', ...
        'ParentID', ...
        'CompressedData', ...
        'CompressedDataSize', ...
        'BinaryData', ...
        'BinaryDataByteOrderMSB', ...
        'ElementByteOrderMSB', ...
        'Color', ...
        'Offset', ...
        'TransformMatrix', ...
        'CenterOfRotation', ...
        'AnatomicalOrientation', ...
        'ElementSpacing', ...
        'DimSize', ...
        'HeaderSize', ...
        'Modality', ...
        'SequenceID', ...
        'ElementMin', ...
        'ElementMax', ...
        'ElementNumberOfChannels', ...
        'ElementSize', ...
        'ElementType', ...
        'ElementDataFile' }
    tag = char(fieldname);

    if nargin < 1
    	header.(tag) = NaN;
    	continue
    end

    if isfield(header_in, tag)
        header.(tag) = header_in.(tag);
        if strcmpi(tag, 'CompressedData') && header.(tag)
            header.CompressedDataSize = NaN;
        end
        continue
    end

    % Use default or derived values if tag is nonexistent
    switch(tag)
        case 'Comment'
        case 'ObjectType'
            header.(tag) = 'Image';
        case 'TransformType'
        case 'NDims'
            header.(tag) = length(size(image));
        case 'Name'
        case 'ID'
        case 'ParentID'
        case 'CompressedData'
        case 'BinaryData'
            header.(tag) = true;
        case 'BinaryDataByteOrderMSB'
            header.(tag) = false;
        case 'ElementByteOrderMSB'
        case 'Color'
        case 'Offset'
        case 'TransformMatrix'
        case 'CenterOfRotation'
        case 'AnatomicalOrientation'
        case 'ElementSpacing'
            header.(tag) = ones(1,length(size(image)));
        case 'DimSize'
            header.(tag) = size(image);
        case 'HeaderSize'
        case 'Modality'
        case 'SequenceID'
        case 'ElementMin'
        case 'ElementMax'
        case 'ElementNumberOfChannels'
        case 'ElementSize'
        case 'ElementType'
            header.(tag) = class(image);
        case 'ElementDataFile'
            [~, name, ~] = fileparts(filepath);
            header.(tag) = sprintf('%s.raw', name);
    end
end
header_out = header;

if nargin < 1
    return
end


% -----------
% Write data
% -----------
[pathstr, ~, ~] = fileparts(filepath);
if isempty(pathstr)
    filepath_data = header.ElementDataFile;
else
    filepath_data = [pathstr filesep header.ElementDataFile];
end
fid = fopen(filepath_data, 'w');

if isfield(header, 'HeaderSize')
    fseek(fid, header.HeaderSize, 'bof');
else
    frewind(fid);
end

if ~isfield(header, 'CompressedData') || ~header.CompressedData
    if isfield(header, 'CompressedDataSize')
        header = rmfield(header, 'CompressedDataSize');
    end
    fwrite(fid, image(:), header.ElementType);
else
    image_compressed = zlibcompress(image);
    fwrite(fid, image_compressed, 'uchar');
end
fclose(fid);


% -------------
% Write header
% -------------
fid = fopen(filepath, 'wt');

% Typecast tag values to expected types
for name = fieldnames(header)'
    tag = char(name);
    switch(tag)
        case 'Comment'
        case 'ObjectType'
        case 'TransformType'
        case 'NDims'
            header.(tag) = sprintf('%i', header.(tag));
        case 'Name'
        case 'ID'
        case 'ParentID'
        case 'CompressedData'
            if header.(tag); value = 'True'; else value = 'False'; end;
            header.(tag) = value;
        case 'CompressedDataSize'
            header.(tag) = sprintf('%i', length(image_compressed));
        case 'BinaryData'
            if header.(tag); value = 'True'; else value = 'False'; end;
            header.(tag) = value;
        case 'BinaryDataByteOrderMSB'
            if header.(tag); value = 'True'; else value = 'False'; end;
            header.(tag) = value;
        case 'ElementByteOrderMSB'
        case 'Color'
        case 'Offset'
            value = sprintf('%g ', header.(tag));
            header.(tag) = value;
        case 'TransformMatrix'
            value = header.(tag)';
            value = sprintf('%g ', value(:)');
            header.(tag) = value;
        case 'CenterOfRotation'
            value = sprintf('%g ', header.(tag));
            header.(tag) = value;
        case 'AnatomicalOrientation'
        case 'ElementSpacing'
            value = sprintf('%g ', header.(tag));
            header.(tag) = value;
        case 'DimSize'
            value = sprintf('%i ', header.(tag));
            header.(tag) = value;
        case 'HeaderSize'
            value = sprintf('%i', header.(tag));
            header.(tag) = value;
        case 'Modality'
        case 'SequenceID'
        case 'ElementMin'
        case 'ElementMax'
        case 'ElementNumberOfChannels'
        case 'ElementSize'
        case 'ElementType'
            switch(header.(tag))
                case 'int8'
                    header.(tag) = 'MET_CHAR';
                case 'uint8'
                    header.(tag) = 'MET_UCHAR';
                case 'int16'
                    header.(tag) = 'MET_SHORT';
                case 'uint16'
                    header.(tag) = 'MET_USHORT';
                case 'int32'
                    header.(tag) = 'MET_INT';
                case 'uint32'
                    header.(tag) = 'MET_UINT';
                case 'single'
                    header.(tag) = 'MET_FLOAT';
                case 'double'
                    header.(tag) = 'MET_DOUBLE';
                otherwise
                    warning('MATLAB:UnknownIdentifier', 'Unhandled element type: %s', header.(tag));
            end
        case 'ElementDataFile'
        otherwise
            warning('MATLAB:UnknownIdentifier', 'Unhandled tag: %s', tag);
    end
    fprintf(fid, '%s = %s\n', tag, header.(tag));
end
fclose(fid);


function compressed = zlibcompress(uncompressed)
% ZLIBCOMPRESS Implements zlib compression.

data = typecast(uncompressed(:), 'uint8');
ostream = java.io.ByteArrayOutputStream();
deflater = java.util.zip.DeflaterOutputStream(ostream);
deflater.write(data);
deflater.close();
compressed = typecast(ostream.toByteArray(), 'uint8');
