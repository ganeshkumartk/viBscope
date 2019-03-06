//Matlab FFT plot
//Done as part of Pilot project in Course C & S
//vIbscope


close all
clear all

%Get filename and path 
    [fname,pathname] = uigetfile('.csv','Select CSV File to Load, Plot, Compute RMS & FFT');
    disp([pathname fname])

%Load CSV
    tic %start timer
    data = csvread([pathname fname]); 
    fprintf('%4.2f seconds - Time to Load Data\n',toc)
    
%Determine variables and Display size
    [N,m] = size(data);
    t = data(:,1); %time in seconds
    x = data(:,2); %array of data for RMS and FFT
    Fs = 1/(t(2)-t(1));
    fprintf('%12.0f data points\n',N)

%Plot Data
    tic %start timer
    figure(1)
    plot(t,x)
    xlabel('Time (s)');
    ylabel('Accel (g)');
    title(fname);
    grid on;
    fprintf('%4.2f seconds - Time to Plot Data\n',toc)
    
%Determine RMS and Plot
    tic %start timer
    w = floor(Fs); %width of the window for computing RMS
    steps = floor(N/w); %Number of steps for RMS
    t_RMS = zeros(steps,1); %Create array for RMS time values
    x_RMS = zeros(steps,1); %Create array for RMS values
    for i=1:steps
        range = ((i-1)*w+1):(i*w);
        t_RMS(i) = mean(t(range));
        x_RMS(i) = sqrt(mean(x(range).^2));  
    end
    figure(2)
    plot(t_RMS,x_RMS)
    xlabel('Time (s)');
    ylabel('RMS Accel (g)');
    title(['RMS - ' fname]);
    grid on;
    fprintf('%4.2f seconds - Time to Compute RMS and Plot\n',toc)    
    
%Determine FFT and Plot
    tic 
    freq = 0:Fs/length(x):Fs/2; %frequency array for FFT
    xdft = fft(x); %Compute FFT
    xdft = 1/length(x).*xdft; %Normalize
    xdft(2:end-1) = 2*xdft(2:end-1); 
    figure(3)
    plot(freq,abs(xdft(1:floor(N/2)+1)))
    xlabel('Frequency (Hz)');
    ylabel('Accel (g)');
    title(['FFT - ' fname]);
    grid on;
    fprintf('%4.2f seconds - Time to Compute FFT and Plot\n',toc)