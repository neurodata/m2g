% W Gray Roncal
% 01.14.2015
% Script to compare KKI42 test retest data and plot result
% Scans are reordered so that both scans for each subject appear together
% Data (covariates and small graphs are from the public ftp site)
% openconnecto.me/data/public/MR/MIGRAINE_v1_0/KKI-42/
files = dir('*.mat');

temp = importdata('kki42_subjectinformation.csv');

for i = 2:length(temp)
    reorderIdx(i-1) = str2num(temp{i}(end-1:end));
end

c = 1;
for i = reorderIdx
    temp = load(files(i).name);
    tgraph = log10(full(temp.graph));
    tgraph(isinf(tgraph))=0;
    smg(:,:,c) = tgraph;
    
    c = c+1;
end

for i = 1:size(smg,3)
    for j = 1:size(smg,3)
        gErr(i,j) = norm(smg(:,:,i)-smg(:,:,j),'fro');
    end
end

figure, imagesc(gErr), colorbar

matches = 0;
for i = 1:1:size(gErr,1)
    temp = sort(gErr(i,:));
    q = i-1+2*mod(i,2);
    matches = matches + (temp(2)==gErr(i,q));
end
matches
possible_matches = size(smg,3)