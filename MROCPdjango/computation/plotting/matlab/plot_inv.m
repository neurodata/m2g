
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

% Author: Disa Mhembere
% Plot all invariants using sweet MATLAB 3D plots.
% Date: 11/26/2013
% Caveat: Only works given the correct data input files

%% Get the eigenvalues
clear; clc
subplot(2,3,1); 
inv = load('F:mrdata\eigs_data.mat');

inv = inv.data;
%figure('Name', 'Eigendecomp');
surfl(inv);
shading interp
colormap(copper);
zlim([0 12]);
grid off;
set(gca, 'fontsize', 14);
set(gca, 'FontWeight', 'bold');
set(gca,'FontName', 'Times');
xlabel('Eigenvalue Rank');
zlabel('Magnitude \times 10^4');
ylabel('Sample');
axis('tight')
set(gca,'YTick', 0:50:114);

set(gca,'YTickLabel',{1:50:100})

%% Get CC
%clear; clc
subplot(2,3,2); 
inv = load_inv('F:mrdata\ClustCoeffinterp_data.mat');

m = get_mat_from_cell(inv);
% create a nice 3d image of the invariant
%figure('Name', 'Clustering Coefficient');
plot_with_params(m, 14);
zlim([0 .04]);
ylim = ([0 size(m,1)]);
xlabel('Log Clustering Coefficient Vector');
zlabel('Percent'); 
ylabel('Sample');
axis('tight');
set(gca,'YTick', 0:50:114);
set(gca,'XTickLabel',{-5:5:10});


%% Get SS-1
%clear; clc
subplot(2,3,3); 
inv = load_inv('F:mrdata\ScanStat1interp_data.mat');

m = get_mat_from_cell(inv);
% create a nice 3d image of the invariant
%figure('Name', 'Scan Statistic');
plot_with_params(m, 14);
xlabel('Log Scan Statistic-1 Vector');
zlabel('Percent'); 
ylabel('Sample');
axis('tight');
set(gca,'YTick', 0:50:114);
set(gca,'XTickLabel',{4:2:16});

%% Get Deg
%clear; clc
subplot(2,3,4); 
inv = load_inv('F:mrdata\Degreeinterp_data.mat');

m = get_mat_from_cell(inv);
% create a nice 3d image of the invariant
%figure('Name', 'Degree');
plot_with_params(m, 14);
xlabel('Log Degree Vector');
zlabel('Percent'); 
ylabel('Sample');
axis('tight');
set(gca,'YTick', 0:50:114);
set(gca,'XTickLabel',{2:2:10});

%% Get Triangles
%clear; clc
subplot(2,3,5);

inv = load_inv('F:mrdata\Triangleinterp_data.mat');

m = get_mat_from_cell(inv);
% create a nice 3d image of the invariant
%figure('Name', 'Degree');
plot_with_params(m, 14);
xlabel('Log Number of Local 3-Cliques Vector');
zlabel('Percent'); 
ylabel('Sample');
axis('tight');
set(gca,'YTick', 0:50:114);
set(gca,'XTickLabel',{5:5:30})

%% Get Global Edges
%clear; clc
subplot(2,3,6); 
male = load('F:mrdata\Edgedata.mat'); male = male.data;
%female = load('F:mrdata\Global_edges_data_1.mat'); female = female.data;
malex = load('F:mrdata\Edgedatax.mat'); malex = malex.data;
%femalex = load('F:mrdata\Globalx_edges_data1.mat'); femalex = femalex.data;

m = NaN(3, size(male,2));
for i=1:size(m,1)
    m(i,:)=male;
end
%figure('Name', 'Global Edges');
surfl(m)
shading interp
colormap copper;
grid off;
set(gca, 'fontsize', 14);
set(gca, 'FontWeight', 'bold');
set(gca,'FontName', 'Times');
xlabel('Log Global Edges');
zlabel('Frequency');
axis('tight')

set(gca,'YTick', 50:114); % Get rid of labels
set(gca,'XTick', 0:20:80);
set(gca,'XTickLabel',{17.2:.3:18.2})

% m = NaN(size(malex,2), size(male,2), 3); % x, y, z
% 
% for x=1:size(m,1)
%     m(x,:,:) = malex
%     m(i,:)=male;
% end