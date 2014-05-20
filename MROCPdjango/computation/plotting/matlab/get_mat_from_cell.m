
% Copyright 2014 Open Connectome Project (http://openconnecto.me)
%
% Licensed under the Apache License, Version 2.0 (the "License");
% you may not use this file except in compliance with the License.
% You may obtain a copy of the License at
%
%     http://www.apache.org/licenses/LICENSE-2.0
%
% Unless required by applicable law or agreed to in writing, software
% distributed under the License is distributed on an "AS IS" BASIS,
% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
% See the License for the specific language governing permissions and
% limitations under the License.
%

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