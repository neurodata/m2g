%% 
% Author: Disa Mhembere
% Date: 11/26/2013
% Load an invariant object which is a 1x1 struct with a data element that is a cell

function inv = load_inv(fn)
    if ~exist(fn, 'file')
        error('file %s not found', fn);
    end
    fprintf('Loading file %s\n', fn);
    inv =  load(fn);
    inv = inv.data;
end
