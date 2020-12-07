R=1024;
MAT=1024;
BW=1000e9;
CT=10e-9;
hold off
syms x y
%TPpim =((R*MAT)/(CC*CT))/(1e9);
%TPcpu =(BW/DIO)/(1e9);
%TPcombined =(1/((1/((R*MAT)/(CC*CT))/(1e9))+(1/(BW/DIO)/(1e9))));
f(x,y) = COMBthroughput(R,MAT,x,CT,BW,y);

%f(x,y) =(1/((1/((R*MAT)/(x*CT)))+(1/(BW/y))));
fsurf(f,[-1 16024 -1 1024],'MeshDensity',38)

set(gca,'yScale','log')
set(gca,'xScale','log')
 

set(gca,'ColorScale','log')
colorbar

view(0,90)
xlabel('CC')
ylabel('DIO')

%%

function [outputArg1] = COMBthroughput(R_slider,MATs_slider,CC_slider,CT_slider,BW_slider,DIO_slider)
TPpim =((R_slider*MATs_slider)/(CC_slider*CT_slider));%/(1e9);
TPcpu =(BW_slider/DIO_slider);%/(1e9);
TPcombined =(1/((1/TPpim)+(1/TPcpu)))/(1e9);

outputArg1 = TPcombined;
end

