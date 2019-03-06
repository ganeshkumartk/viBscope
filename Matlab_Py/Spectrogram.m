//Matlab FFT plot
//Done as part of Pilot project in Course C & S
//vIbscope


function [x_3D, y_3D, z_3D] = Mide_Spectrogram(datalist,fActual,nSlicesPerSecond)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%[x_3D, y_3D, z_3D] = FFT_PSD_Spectrogram(datalist,fActual,nSlicesPerSecond)
% Given a dataset this will calculate the spectrogram
%
% Inputs:
%   datalist = two column array with time in first column, data to analyze
%       in second
%   fActual = sample rate of the data in Hertz
%   nSlicesPerSecond = number of slices per second to break up spectrogram
%
% Outputs:
%   x_3D = time for spectrogram
%   y_3D = frequency for spectrogram
%   z_3D = amplitude for spectrogram
%
%MATLAB may run out of memory for large files
%
%Mide Technology
%Date: 06.08.2016
%Rev: 1
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%Compute Spectrogram
    nPts=length(datalist(:,1));
    yfft=datalist(:,2);
    nPointsPerSlice=floor(fActual / nSlicesPerSecond);

    % for very short recordings or stupid values of nSlicesPerSecond,
    % nPointsPerSlice may end up being ouside a legal range for the actual
    % data series. In this case, warn and pick a sane value. Sliced data may
    % not render usefully, but avoid throwing a runtime error.
        if(nPointsPerSlice == 0 || nPointsPerSlice > nPts)
            disp('nPointsPerSlice cannot be achieved; slicing adjusted.');
            nPointsPerSlice = nPts/4;
        end

    % Now try to slice/reshape the column vector to (x columns of nPointsPerSlice points each)
    % in such a way that it reshapes cleanly. We'll throw away up to 1 slice of data, but we
    % avoid reshape barfing up an error here.
        yfft=reshape(yfft([1:floor(length(yfft)/nPointsPerSlice)*nPointsPerSlice]),nPointsPerSlice,[]);
        [fftrows,fftcols]=size(yfft);

    % create the lone X vector to scale these all against...
        x=[0:fftrows-1];
        recordSliceTime=datalist(fftrows,1) - datalist(1,1); % again, accurately get the elapsed time of each slice
        recordSliceTime=recordSliceTime+(recordSliceTime/fftrows); % ...
        x = x .* (1/recordSliceTime);  % normalize frequency according to sample rate and nPts

    % Apply hamming window: w(n) = 0.53836 - .46164*cos(2*pi*n/N-1)
        window=[1:fftrows];
        windowy = (0.53836 - .46164*cos((2*pi*window(:)) ./ (length(window)-1)));

    yabs=yfft;  % pre-allocate yabs with same size as yfft

    for j=[1:fftcols]
        %yfft(:,j)=fft(yfft(:,j) );                     % not windowed
        yfft(:,j)=fft(yfft(:,j) .* windowy(:));         % windowed
        %yabs(:,j)=yfft(:,j).*conj(yfft(:,j)) / length(yfft(:,j));
        yabs(:,j)=abs(yfft(:,j)) / (0.5*length(yfft(:,j)));
        yabs(1,j)=0;	% Get rid of DC component
        %yabs(2,j)=0;	% Get rid of DC component
        %yabs(3,j)=0;	% Get rid of DC component
    end


    % Create reasonable default values for 'points of interest'. This is
    % the section of the plot we will actually show.
        nPointsOfInterest=nPointsPerSlice /2;
        startPointOfInterest=1;
        endPointOfInterest=nPointsOfInterest;

    % if user entered invalid frequency values, constrain them to a range the plot actually contains
        if(startPointOfInterest < 0)
            startPointOfInterest = 0;
        end
        if(endPointOfInterest > length(x)/2)
            endPointOfInterest = length(x)/2; % do not show user aliased data
        end

    % finally, actually make the plot!
        x_3D = [1:fftcols] / nSlicesPerSecond;
        y_3D = x([startPointOfInterest+1:endPointOfInterest+1]);
        z_3D = yabs([startPointOfInterest+1:endPointOfInterest+1],:);


