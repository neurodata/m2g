% Brain Volume Visualization
% W. Gray Roncal, Version 0.3, 02/08/2014

% NOTE THAT LABELS IN LABEL FILE MATCH DESIKAN
% MEANING 1-35, 101-135!!!
% This requires ReadXML, found in the MR git repo


%% Load data

%This corresponds to MNI file for this data
labels = ReadXml('MNI152_T1_1mm_brain_labels.xml');

% Optional, but recommended - trim these with brain mask
% to avoid using dilated labels
mask = ReadXml('MNI152_T1_1mm_brain_mask.xml');
labels(mask == 0) = 0;

% These are the nodes, 1-70
%use original label space, 1-indexed
for i = 1:135
    idx = find(labels == i);
    
    %unexpected behavior when doing this directly, so using ind2sub
    %to be more explicit
    [x,y,z] = ind2sub(size(labels),idx);
    centroid(i,:) = [mean(x),mean(y),mean(z)];
end

%trim labels that don't exist, convert to 1-70 convention
centroid = centroid([1:35,101:135],:);

%Optional
centroid = round(centroid);

%% Now do brain setup - in gray

hfig = figure(100);
set(hfig,'PaperOrientation','Landscape');
set(gcf,'Color',[1 1 1])

h3a = isosurface(labels,0);
h3b = reducepatch(h3a, 0.1);
h3 = patch(h3b);

% You may want to play with these parameters. 
set(h3,'FaceColor',[0.2, 0.2 0.2],'EdgeColor','none','FaceAlpha',0.05,'FaceLighting','phong')

%% OR  do brain setup - in color
% There's a better way to do all the regions in one go with meshgrid 
% and isocolor, but this works

hfig = figure(100);
set(hfig,'PaperOrientation','Landscape');
set(gcf,'Color',[1 1 1])
hold on
nColors = 16;
cmap = jet(nColors); %choose your colormap

for i = [1:35, 101:135]
    reg = labels;
    reg(reg ~= i) = 0;
    h3a = isosurface(reg,0);
    h3b = reducepatch(h3a, 0.1);
    h3 = patch(h3b);
    %set facealpha if this is too strong.
    set(h3,'FaceColor',cmap(mod(i,nColors)+1,:),'EdgeColor','none','FaceAlpha',0.07,'FaceLighting','phong')
    drawnow
end
    
set(gca,'visible','off');
hold off
%daspect([1 1 1]);axis tight
%camlight;


%% TODO Your fancy weighted edges go here!!
hold on
for i = 1:70
    plot3(centroid(i,2),centroid(i,1),centroid(i,3),'.k', 'MarkerSize', 20)
end
hold off
%% Visualization

% I like these three views - you may wamt to play with
% these orientations to get something in cardinal axes
set(gca,'visible','off');%'XTick',[],'YTick',[],'ZTick',[]);
set(gca,'view',[90, 90])
axis tight
axis square

set(gca,'view',[-90, 0])
axis tight
axis square

set(gca,'view',[0, 0])
axis tight
axis square

%some sort of imwrite or print statement here




