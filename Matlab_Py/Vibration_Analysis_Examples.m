//Matlab FFT plot
//Done as part of Pilot project in Course C & S
//vIbscope



close all
clear all

%% Very simple 60 Hz signal with callouts
%Create simple sine wave and plot
    f = 60;
    t = (0:.0001:1)/60;
    y = sin(2*pi*f*t);
    fig = figure('Name','Simple 60 Hz Sine Wave','NumberTitle','off');
    plot(t,y,'LineWidth',2)
    xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Simple 60 Hz Sine Wave');
    grid on
    hold all
    plot([0 1/60],[1/2^.5 1/2^.5], 'r--','LineWidth',2) %plot horizontal line at RMS
        
    %Amplitude
        x = 1/60/4;
        yy = .5;
        w = .004;
        ah = annotation('doublearrow','LineWidth',1.25,'Color',[.4 .4 .4]);
        set(ah,'parent',gca);
        set(ah,'position',[x 0 0 1]);
        ah = annotation('rectangle','FaceColor',[1 1 1],'LineWidth',1.25,'Color',[.4 .4 .4]);
        set(ah,'parent',gca);
        set(ah,'position',[x-w/2 yy-.06 w .12]);
        text(x,yy,'Amplitude','fontsize',11,'horizontalAlignment', 'center','Color',[.4 .4 .4]);
        
    %Peak to Peak
        x = 1/60;
        yy = -.5;
        w = .005;
        ah = annotation('doublearrow','LineWidth',1.25,'Color',[.4 .4 .4]);
        set(ah,'parent',gca);
        set(ah,'position',[x -1 0 2]);
        ah = annotation('rectangle','FaceColor',[1 1 1],'LineWidth',1.25,'Color',[.4 .4 .4]);
        set(ah,'parent',gca);
        set(ah,'position',[x-w/2 yy-.06 w .12]);
        text(x,yy,'Peak to Peak','fontsize',11,'horizontalAlignment', 'center','Color',[.4 .4 .4]);            
        
    %Period
        x = 1/60/2;
        yy = 0;
        w = .005;
        ah = annotation('doublearrow','LineWidth',1.25,'Color',[.4 .4 .4]);
        set(ah,'parent',gca);
        set(ah,'position',[0 0 1/60 0]);
        ah = annotation('rectangle','FaceColor',[1 1 1],'LineWidth',1.25,'Color',[.4 .4 .4]);
        plot([0 1/60],[0 0], 'LineWidth',1.25,'Color',[.4 .4 .4]) %correct line scaling issue
        set(ah,'parent',gca);
        set(ah,'position',[x-w/2 yy-.06 w .12]);
        text(x,yy,'Period = 1/f','fontsize',11,'horizontalAlignment', 'center','Color',[.4 .4 .4]);            
        
    %RMS
        x = 3/60/4;
        yy = 1/2^.5/2;
        w = .002;
        ah = annotation('doublearrow','LineWidth',1.25,'Color',[.4 .4 .4]);
        set(ah,'parent',gca);
        set(ah,'position',[x 0 0 1/2^.5]);
        ah = annotation('rectangle','FaceColor',[1 1 1],'LineWidth',1.25,'Color',[.4 .4 .4]);
        set(ah,'parent',gca);
        set(ah,'position',[x-w/2 yy-.06 w .12]);
        text(x,yy,'RMS','fontsize',11,'horizontalAlignment', 'center','Color',[.4 .4 .4]);   

    xlim([0 0.02])
    set(fig,'color', 'white','units','points','position',[100, 100, 500, 375]);
    %print('sine-wave-amplitude-rms-peak-to-peak-period','-dsvg')
    %print('sine-wave-amplitude-rms-peak-to-peak-period','-djpeg')
        
%% Simple fabricated waveform example with spectrum analysis
    %Create simple 60 Hz sine wave with a 22 Hz component and 100 Hz components and plot FFT
        f1 = 60;
        f2 = 22;
        f3 = 100;
        fs = 500;                              % Sample frequency (Hz)
        t = 0:1/fs:.5-1/fs;                     
        x = 2*sin(2*pi*f1*t) + 1*sin(2*pi*f2*t)+ 1.5*sin(2*pi*f3*t);
        sub = 1:50; %plot first 50 points
        data = t';
        data(:,2) = x';

        fig = figure('Name','Simple Waveform Example','NumberTitle','off');
        %plot first 100 points
        subplot(3,2,1)
            plot(data(sub,1),data(sub,2),'LineWidth',1.2)
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Short Simple Waveform');
            grid on
        subplot(3,2,2)
            [freq, xdft] = Mide_FFT_PSD(data(sub,:),fs);
            plot(freq,xdft,'LineWidth',1.2)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Short Simple Waveform');
            grid on
        %do full 1 second (1000 points)
        subplot(3,2,3)
            plot(data(:,1),data(:,2),'LineWidth',1)
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Extended Simple Waveform');
            grid on
        subplot(3,2,4)
            [freq, xdft] = Mide_FFT_PSD(data,fs);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Extended Simple Waveform');
            grid on
            ylim([0 2])
        %add noise
        data(:,2) = data(:,2) + 1.5*gallery('normaldata',size(t),4)';
        subplot(3,2,5)
            plot(data(:,1),data(:,2),'LineWidth',1)
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Added Noise');
            grid on
        subplot(3,2,6)
            [freq, xdft] = Mide_FFT_PSD(data,fs);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Waveform w/ Noise');
            grid on
        set(fig,'color', 'white','units','points','position',[100, 100, 750, 500]);
        %print('fast-fourier-transform-(FFT)-example','-dsvg')
        %print('fast-fourier-transform-(FFT)-example','-djpeg')
    
%% Car engine data from http://www.mide.com/pages/slam-stick-how-to-videos
    %Load 
        load('Vibe-LOG-0002-025G-DC-PC_01.mat');
        car = zeros(length(ADC),2);
        car(:,1) = ADC(1,:)';
        car(:,2) = ADC(4,:)'; %z axis
        f_s_car = 1/(car(2,1)-car(1,1));
        
	%Plot idle time of car data then FFT
        fig = figure('Name','Car Engine Idle Example','NumberTitle','off');
        sub = (45*20000):(50*20000);
        subplot(2,1,1)
            plot(car(sub(1:1000),1),car(sub(1:1000),2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Vibration of Car Engine during Idle (Zoomed In)');
            xlim([46 46.05])
            grid on
        subplot(2,1,2)
            [freq, xdft] = Mide_FFT_PSD(car(sub,:),f_s_car);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Car Engine during Idle');
            grid on
            xlim([0 500])
        set(fig,'color', 'white','units','points','position',[100, 100, 500, 500]);
        %print('car-engine-FFT-example','-dsvg')
        %print('car-engine-FFT-example','-djpeg')

    %Plot entire car data then spectrogram of entire dataset
        fig = figure('Name','Car Engine Example','NumberTitle','off');
        subplot(2,1,1)
            plot(car(:,1),car(:,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Vibration of Car Engine');
            grid on
        subplot(2,1,2)
            [x_3D, y_3D, z_3D] = Mide_Spectrogram(car,f_s_car,4);
            surf(x_3D, y_3D, log(z_3D),'EdgeColor','none') %surface plot with amplitude on a log scale
            xlabel('Time (s)'); ylabel('Frequency (Hz)'); zlabel('Amplitude'); title('Spectrogram of Car Engine');
            grid on
            ylim([0 500]) %only plot to 500 Hz
            view(2)
        set(fig,'color', 'white','units','points','position',[100, 100, 1000, 500]);
        %print('car-engine-spectrogram-example','-dsvg')
        %print('car-engine-spectrogram-example','-djpeg')

    %Compare spectrogram to FFT
        fig = figure('Name','Car Engine FFT Example of Changing Signal','NumberTitle','off');
        subplot(2,1,1)
            plot(car(:,1),car(:,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Vibration of Car Engine');
            grid on
        subplot(2,1,2)
            [freq, xdft] = Mide_FFT_PSD(car,f_s_car);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Car Engine during Idle and Revving');
            grid on
            xlim([0 500])
        set(fig,'color', 'white','units','points','position',[100, 100, 500, 500]);
        %print('car-engine-fft-long-example','-dsvg')
        %print('car-engine-fft-long-example','-djpeg')        
                
%% Truck Bed Vibration
    %Load 
        load('Truck_Bed_01.mat');
        truck = zeros(length(ADC),2);
        truck(:,1) = ADC(1,:)'-ADC(1,1);
        truck(:,2) = ADC(4,:)'; %z axis data
        f_s_truck = 1/(truck(2,1)-truck(1,1));
        
    %Plot entire car data then spectrogram of entire dataset
        fig = figure('Name','Truck Bed Vibration','NumberTitle','off');
        subplot(2,1,1)
            plot(truck(:,1),truck(:,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Vibration on Truck Bed');
            grid on
        subplot(2,1,2)
            [x_3D, y_3D, z_3D] = Mide_Spectrogram(truck,f_s_truck,4);
            surf(x_3D, y_3D, log(z_3D),'EdgeColor','none') %surface plot with amplitude on a log scale
            xlabel('Time (s)'); ylabel('Frequency (Hz)'); zlabel('Amplitude'); title('Spectrogram of Truck Bed');
            grid on
            ylim([0 200]) %only plot to 200 Hz
            view(2)
        set(fig,'color', 'white','units','points','position',[100, 100, 1000, 500]);
        %print('truck-bed-spectrogram-example','-dsvg')
        %print('truck-bed-spectrogram-example','-djpeg')
        
    %Plot vibration during regular operation (no shocks)
        fig = figure('Name','Truck Bed Vibration Example','NumberTitle','off');
        sub = (450*5000):(452*5000);
        subplot(2,1,1)
            plot(truck(sub,1),truck(sub,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Vibration on Truck Bed Zoomed In ');
            xlim([450 452])
            grid on
        subplot(2,1,2)
            [freq, xdft] = Mide_FFT_PSD(truck(sub,:),f_s_truck);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of General Truck Bed Vibration');
            grid on
            xlim([0 100])
        set(fig,'color', 'white','units','points','position',[100, 100, 500, 500]);
        %print('truck-bed-FFT-example','-dsvg')
        %print('truck-bed-FFT-example','-djpeg')    
        
%% Random Vibration (MIL-STD-810G Fig 514.6C-5)
    %Load data from Slam Stick X 
        load('Random_Y_01.mat'); %time, x axis, y axis, z axis
        SSX_random = zeros(length(ADC),2);
        SSX_random(:,1) = ADC(1,:)';
        SSX_random(:,2) = ADC(3,:)';
        f_s_random = 1/(SSX_random(2,1)-SSX_random(1,1));
    %Load control PSD data
        psd_control = csvread('PSD_random_control.csv');

    sub1 = 1:1000; %subset of 1,000 points
    sub2 = 1:10000; %subset of 10,000 points
    sub3 = 1:100000; %subset of 100,000 points

    %Plot time domain of data for different subsets
        fig = figure('Name','MIL-STD-810G Fig 514.6C-5 Slam Stick Data','NumberTitle','off');
        subplot(3,1,1)
            plot(SSX_random(sub1,1),SSX_random(sub1,2),'LineWidth',1)
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('1,000 points of MIL-STD-810G Jet Aircraft Cargo Vibration Exposure');
            grid on
        subplot(3,1,2)
            plot(SSX_random(sub2,1),SSX_random(sub2,2),'LineWidth',1)
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('10,000 points of MIL-STD-810G Jet Aircraft Cargo Vibration Exposure');
            grid on
        subplot(3,1,3)
            plot(SSX_random(sub3,1),SSX_random(sub3,2),'LineWidth',1)
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('100,000 points of MIL-STD-810G Jet Aircraft Cargo Vibration Exposure');
            grid on
            ylim([-20 20])
        set(fig,'color', 'white','units','points','position',[100, 100, 750, 375]);
        %print('jet-aircraft-cargo-vibration-exposure','-dsvg')
        %print('jet-aircraft-cargo-vibration-exposure','-djpeg')    
        
    %Compute and plot a comparison of the FFT and PSD for different time
    %ranges
        [freq1, xdft1, psdx1] = Mide_FFT_PSD(SSX_random(sub1,:),f_s_random);
        [freq2, xdft2, psdx2] = Mide_FFT_PSD(SSX_random(sub2,:),f_s_random);
        [freq3, xdft3, psdx3] = Mide_FFT_PSD(SSX_random(sub3,:),f_s_random);
        
        fig = figure('Name','MIL-STD-810G Fig 514.6C-5  Slam Stick FFT and PSD Data','NumberTitle','off');
        subplot(3,2,1)
            loglog(freq1,xdft1,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of 1,000 points');
            grid on
            ylim([10^(-4) 1])
            xlim([10 10000])
        subplot(3,2,3)
            loglog(freq2,xdft2,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of 10,000 points');
            grid on
            ylim([10^(-4) 1])
            xlim([10 10000])
        subplot(3,2,5)
            loglog(freq3,xdft3,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of 100,000 points');
            grid on
            ylim([10^(-4) 1])
            xlim([10 10000])
        subplot(3,2,2)
            loglog(freq1,psdx1,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD of 1,000 points');
            grid on
            hold all;
            loglog(psd_control(:,1),psd_control(:,3),'LineWidth',2,'Color','r')     
            loglog(psd_control(:,1),psd_control(:,4),'LineWidth',2,'Color','r')      
            ylim([10^(-5) .1])
            xlim([10 10000])
        subplot(3,2,4)
            loglog(freq2,psdx2,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD of 10,000 points');
            grid on
            hold all;
            loglog(psd_control(:,1),psd_control(:,3),'LineWidth',2,'Color','r')     
            loglog(psd_control(:,1),psd_control(:,4),'LineWidth',2,'Color','r')      
            ylim([10^(-5) .1])
            xlim([10 10000])
        subplot(3,2,6)
            loglog(freq3,psdx3,'.','LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD of 100,000 points');
            grid on
            hold all;
            loglog(psd_control(:,1),psd_control(:,3),'LineWidth',2,'Color','r')     
            loglog(psd_control(:,1),psd_control(:,4), 'LineWidth',2,'Color','r')      
            ylim([10^(-5) .1])
            xlim([10 10000])
        set(fig,'color', 'white','units','points','position',[100, 0, 750, 700]);
        %print('jet-aircraft-cargo-vibration-PSD','-dsvg')
        %print('jet-aircraft-cargo-vibration-PSD','-djpeg')
       
%% Random Vibration generated on commercial airplane during cruise
    %Load 
        load('Airplane_Random_Vibration_Cruise_01.mat');
        airplane = zeros(length(ADC),2);
        airplane(:,1) = ADC(1,:)';
        airplane(:,2) = ADC(4,:)';
        f_s_airplane = 1/(airplane(2,1)-airplane(1,1));
        
	%Plot idle time of car data then FFT
        fig = figure('Name','Airplane Vibration During Cruise Example','NumberTitle','off');
        subplot(2,1,1)
            plot(airplane(1:2000,1),airplane(1:2000,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Airplane Vibration During Cruise (Zoomed In)');
            grid on
            xlim([1075 1075.5])
        subplot(2,1,2)
            [freq, xdft, psdx] = Mide_FFT_PSD(airplane,f_s_airplane);
            loglog(freq,psdx,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD of Airplane Vibration During Cruise');
            grid on
            xlim([1 1000])
        set(fig,'color', 'white','units','points','position',[100, 100, 500, 500]);
        %print('airplane-psd-example','-dsvg')
        %print('airplane-psd-example','-djpeg')
%% Aircraft Vibration (Slam Stick on the outside of an aircraft)
    %Load 
        load('Aircraft_Vibration_01.mat');
        aircraft = zeros(length(ADC),2);
        aircraft(:,1) = ADC(1,:)'-ADC(1,1);
        aircraft(:,2) = ADC(4,:)'; %z axis data
        f_s_aircraft = 1/(aircraft(2,1)-aircraft(1,1));
        sub1 = 1:10000;
        sub2 = sub1+2500*520.05;
        
    %Plot dataset ranges, FFT, and PSD
        fig = figure('Name','Aircraft Vibration','NumberTitle','off');
        subplot(3,3,1)
            plot(aircraft(sub1,1),aircraft(sub1,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Subset 1 of Vibration on Aircraft');
            grid on
        subplot(3,3,4)
            plot(aircraft(sub2,1),aircraft(sub2,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Subset 2 of Vibration on Aircraft');
            grid on
            xlim([520 524])
        subplot(3,3,7)
            plot(aircraft(:,1),aircraft(:,2))
            xlabel('Time (s)'); ylabel('Amplitude (g)'); title('Entire Data Set of Vibration on Aircraft');
            grid on
        subplot(3,3,2)
            [freq, xdft, psdx] = Mide_FFT_PSD(aircraft(sub1,:),f_s_aircraft);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Aircraft Vibration 1');
            grid on
            xlim([0 600])            
        subplot(3,3,3)
            loglog(freq,psdx,'LineWidth',1)
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD of Aircraft Vibration 1');
            grid on
            xlim([1 1000])
        subplot(3,3,5)
            [freq, xdft, psdx] = Mide_FFT_PSD(aircraft(sub2,:),f_s_aircraft);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Aircraft Vibration 2');
            grid on
            xlim([0 600])            
        subplot(3,3,6)
            loglog(freq,psdx,'LineWidth',1)
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD of Aircraft Vibration 2');
            grid on
            xlim([1 1000])
        subplot(3,3,8)
            [freq, xdft, psdx] = Mide_FFT_PSD(aircraft,f_s_aircraft);
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT of Aircraft Vibration Entire');
            grid on
            xlim([0 600])            
        subplot(3,3,9)
            loglog(freq,psdx,'LineWidth',1)
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD of Aircraft Vibration Entire');
            grid on
            xlim([1 1000])
        set(fig,'color', 'white','units','points','position',[100, 100, 1200, 600]);
        %print('aircraft-vibration-fft-psd-example','-dsvg')
        %print('aircraft-vibration-fft-psd-example','-djpeg')
    %Plot FFT, PSD, and Spectrogram
        fig = figure('Name','Aircraft Vibration FFT, PSD, Spectrogram','NumberTitle','off');
        subplot(1,4,1)
            plot(freq,xdft,'LineWidth',1)  
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g)'); title('FFT');
            grid on
            xlim([0 600])            
        subplot(1,4,2)
            loglog(freq,psdx,'LineWidth',1)
            xlabel('Frequency (Hz)'); ylabel('Amplitude (g^2/Hz)'); title('PSD');
            grid on
            xlim([1 1000])
        subplot(1,4,3:4)
            [x_3D, y_3D, z_3D] = Mide_Spectrogram(aircraft,f_s_aircraft,1);
            surf(x_3D, y_3D, z_3D,'EdgeColor','none')
            xlabel('Time (s)'); ylabel('Frequency (Hz)'); zlabel('Amplitude'); title('Spectrogram of Aircraft Vibration');
            grid on
            ylim([0 600])
            view([60 60])
            colormap(jet)
            caxis([-1,5])       
            zlim([0 4])
        set(fig,'color', 'white','units','points','position',[100, 100, 1200, 300]);
        %print('aircraft-vibration-fft-psd-spectrogram-example','-dsvg')
        %print('aircraft-vibration-fft-psd-spectrogram-example','-djpeg')
    %Plot Just Spectrogram
        fig = figure('Name','Aircraft Vibration Spectrogram','NumberTitle','off');
        surf(x_3D, y_3D, z_3D,'EdgeColor','none')
        xlabel('Time (s)'); ylabel('Frequency (Hz)'); zlabel('Amplitude'); title('Spectrogram of Aircraft Vibration');
        grid on
        ylim([0 600])
        view([60 60])
        colormap(jet)
        caxis([-1,5])
        zlim([0 4])
        set(fig,'color', 'white','units','points','position',[100, 100, 500, 500]);        
        %print('aircraft-vibration-spectrogram-example','-dsvg')
        %print('aircraft-vibration-spectrogram-example','-djpeg')
    %Plot Just Spectrogram in log scale and 2d
        fig = figure('Name','Aircraft Vibration Spectrogram 2D','NumberTitle','off');
        surf(x_3D, y_3D, log(z_3D),'EdgeColor','none')
        xlabel('Time (s)'); ylabel('Frequency (Hz)'); zlabel('Amplitude'); title('2D Spectrogram of Aircraft Vibration');
        grid on
        ylim([0 600])
        view(2)
        set(fig,'color', 'white','units','points','position',[100, 100, 500, 500]);        
        %print('aircraft-vibration-2d-spectrogram-example','-dsvg')
        %print('aircraft-vibration-2d-spectrogram-example','-djpeg')        
        
               