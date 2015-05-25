N=42;
% having smg from run 1 and run 2, I want to reorganize the data into a
% single matrix that interleaves the two....

smgs = zeros(70,70,2*N);
for i = 1:2*N
    if ~mod(i,2)
        smgs(:,:,i) = smg_1(:,:,floor(i/2));
    else
        smgs(:,:,i) = smg_2(:,:,floor(i/2)+1);
    end
end

gErr2 = zeros(2*N, 2*N);
for i = 1:2*N
    for j = 1:2*N
        gErr2(i,j) = norm(smgs(:,:,i)-smgs(:,:,j),'fro');        
    end
end
figure(7)
imagesc(gErr2); colorbar;



% for each scan (1-2*N)
matches = 0;
for i = 1:1:size(gErr2,1)
    temp = sort(gErr2(i,:));
    q = i-1+2*mod(i,2);
    matches = matches + (temp(2)==gErr2(i,q));
end