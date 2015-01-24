function convertMatToNifti(input_mat_file, output_nii_file)
    
    nii = make_nii(input_mat_file);
    
    save_nii(nii,output_nii_file);

    [~, ~, ext] = fileparts(output_nii_file);
    if strcmpi(ext,'.nii') == 1                
        gzip(output_nii_file);   
        delete(output_nii_file);
    end

end
