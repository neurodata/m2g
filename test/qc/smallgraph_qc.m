% smallgraph_qc.m
% G. Kiar
% 02.25.2015
% Compares produced graphs by MIGRAINE and M2G to one another, ensuring
% that QC standards are met (i.e. the graphs are sufficiently similar).
% This will currently be done between the two iterations of the pipeline,
% but will eventually (ideally) be comparing produced graphs to ground
% truth graphs of phantom data. This computes TRT statistics as well as
% distance across pipelines.
% This code has been adapted from W. R. Gray Roncal, 01.14.2015

%% Load subject metadata
temp = importdata('kki42_subjectinformation.csv');
for i = 2:length(temp)
    reorderIdx(i-1) = str2num(temp{i}(end-1:end));
end

%tell me where things are
m2g_dir = 'm2g_from_migrainefibs';
migraine_dir = 'migraine';

%% Load M2G graphs

%directories currently hard coded
cd(m2g_dir)
files = dir('*.mat');
c = 1;
for i = reorderIdx
    temp = load(files(i).name);
    tgraph = log10(full(temp.graph));
    tgraph(isinf(tgraph))=0;
    m2g_sm(:,:,c) = tgraph;
    c = c+1;
end

for j = 1:size(m2g_sm,3)
    for i = 1:size(m2g_sm,3)
        m2g_err(j,i) = norm(m2g_sm(:,:,j)-m2g_sm(:,:,i),'fro');
    end
end

figure, imagesc(m2g_err), colorbar
title('M2G')
cd ..
%% Load MIGRAINE graphs
cd(migraine_dir)
files = dir('*.mat');
c = 1;
for i = reorderIdx
    temp = load(files(i).name);
    tgraph = log10(full(temp.fibergraph));
    tgraph(isinf(tgraph))=0;
    migraine_sm(:,:,c) = tgraph;
    c = c+1;
end

for j = 1:size(m2g_sm,3)
    for i = 1:size(m2g_sm,3)
        migraine_err(j,i) = norm(migraine_sm(:,:,j)-migraine_sm(:,:,i),'fro');
    end
end

figure, imagesc(migraine_err), colorbar
title('MIGRAINE')
cd ..

%% m2g to migraine comparison
for k= 1:size(m2g_sm,3)
    m2g_to_migraine(k) = norm(migraine_sm(:,:,k)-m2g_sm(:,:,k),'fro');
end


%% TRT
matches = 0;
for i = 1:1:size(m2g_gerr,1)
    temp = sort(m2g_gerr(i,:));
    q = i-1+2*mod(i,2);
    temp(2)
    m2g_gerr(i,q)
    matches = matches + (temp(2)==m2g_gerr(i,q));
end
matches
possible_matches = size(m2g_sm,3)