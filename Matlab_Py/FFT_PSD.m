//Matlab FFT plot
//Done as part of Pilot project in Course C & S
//vIbscope




function [freq, xdft, psdx, phase] = Mide_FFT_PSD(datalist,fActual)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%[freq, xdft, psdx, phase] = FFT_PSD_Spectrogram(datalist,fActual)
% Given a dataset this will calculate the FFT PSD and phase
%
% Inputs:
%   datalist = two column array with time in first column, data to analyze
%       in second
%   fActual = sample rate of the data in Hertz
%
% Outputs:
%   freq = frequency bins for FFT and PSD
%   xdft = amplitude of FFT in native units of datalist
%   phase = phase response of FFT in radians
%   psdx = amplitude of FFT in native units of datalist squared divided by
%       Hz
%
%MATLAB may run out of memory for large files
%
%Mide Technology
%Date: 06.08.2016
%Rev: 1
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%Compute FFT & PSD
    Fs = fActual;
    x = datalist(:,2);     
    N = length(x);
    freq = 0:Fs/length(x):Fs/2;
    xdft = fft(x);
    xdft = xdft(1:floor(N/2)+1);
    psdx = (1/(Fs*N)) * abs(xdft).^2;
    psdx(2:end-1) = 2*psdx(2:end-1);
    psdx = psdx';
    xdft = 1/length(x).*xdft;
    xdft(2:end-1) = 2*xdft(2:end-1);
    xdft = xdft';
    phase = unwrap(angle(xdft));
    xdft = abs(xdft);
        
