% Author: Disa Mhembere
% Date: 11/26/2013
% Use this function to plot several invariants with the same plotting parameters to
% avoid code redundancy

function [] = plot_with_params(mat, fontsize)
    surfl(mat);
    shading interp
    colormap(copper);
    grid off;
    set(gca, 'fontsize',fontsize);
    set(gca, 'FontWeight', 'bold');
    set(gca,'FontName', 'Times');
end
