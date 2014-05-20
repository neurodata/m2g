
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
% Load an invariant object which is a 1x1 struct with a data element that is a cell

function inv = load_inv(fn)
    if ~exist(fn, 'file')
        error('file %s not found', fn);
    end
    fprintf('Loading file %s\n', fn);
    inv =  load(fn);
    inv = inv.data;
end