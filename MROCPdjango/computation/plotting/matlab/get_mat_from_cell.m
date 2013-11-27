%% 
% Author: Disa Mhembere
% Date: 11/26/2013
% From a cell create a matrix that we can create a 3D surface from

function m = get_mat_from_cell(inv)
    max_len = 0;
    % Compute max of lengths of the array
    for idx=1:size(inv,2)
        arr = inv(1, idx);
        if size(arr{1,1}, 2) > max_len 
            max_len = size(arr{1,1}, 2);
        end
    end

    m = NaN(size(inv,2), max_len); % create matrix filled with NaNs
    % fill matrix
    for idx=1:size(inv,2)
        arr = inv(1, idx);
        arr = arr{1,1};
        m(idx,1:size(arr,2)) = arr;
    end
end
