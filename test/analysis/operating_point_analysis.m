
files = dir('*.mat');
subjects = 2;
params = 3;
N = subjects*params;

values = [0.2, 0.5, 0.8];

figure (2)
c=1;
for i=1:subjects
    for j=1:params
        temp = load(files(c).name);
        g(:,:,c) = full(temp.graph);
        subplot(subjects, params, c);
        imagesc(log10(g(:,:,c)));
        colorbar; caxis([0 4]);
        tit = strcat('Number of edges:',num2str(sum(sum(g(:,:,c)))));
        tit = strcat(tit, '; b=', num2str(values(mod(c-1,params)+1)));
        title(tit);
        c=c+1;
    end
end