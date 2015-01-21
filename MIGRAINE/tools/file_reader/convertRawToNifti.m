function convertRawToNifti(input_xml_file, output_nii_file)
    try
        tree = xmlread(input_xml_file);
    catch
        error('Failed to read XML file %s.',input_xml_file);
    end
    
    datasetAttributes = tree.getDocumentElement;
    
    attributes = datasetAttributes.getChildNodes;
    
    % Get X,Y,Z dimensions
    dims = attributes.getElementsByTagName('Extents');
    
    dimX = str2double(dims.item(0).getTextContent);
    dimY = str2double(dims.item(1).getTextContent);
    dimZ = str2double(dims.item(2).getTextContent);
    
    dims = [dimX, dimY, dimZ];

    % Get Raw Data Type
    dtype = attributes.getElementsByTagName('Data-type');
    dtype = dtype.item(0).getTextContent;    

    [path,name,ext] = fileparts(input_xml_file);
    
    input_raw_file = strcat(path,'/',name,'.raw');

    disp(dims);
    disp(dtype);
    
    raw_data = openRawFile2(input_raw_file,dims,dtype);
    
    if strcmpi(dtype,'Float') == 1
        dtype = 16;
    elseif strcmpi(dtype,'Short') == 1  
        dtype = 4;
    end
        
    nii = make_nii(raw_data,[1 1 1], [0 0 0], dtype);
    save_nii(nii,output_nii_file);

    [~, ~, ext] = fileparts(output_nii_file);
    if strcmpi(ext,'.nii') == 1                
        gzip(output_nii_file);   
        delete(output_nii_file);
    end

end
