
%% Clears
clear all; clc; fclose all;

%% Load paths
pathCell = regexp(path, pathsep, 'split');
if ispc  % Windows is not case-sensitive
  onPath = any(strcmpi(pwd, pathCell));
else
  onPath = any(strcmp(pwd, pathCell));
end
clear pathCell
if ~onPath
    addpath(genpath(pwd));
end

%% Select Benchmark
dirName = '.\Benchmarks\';
Allfolders = dir(dirName);
fprintf('\nBenchmark networks:\n');
for i=3:length(Allfolders) % ignore '.', '..'
    fprintf([num2str(i-2),'. ', Allfolders(i).name, '\n\n']);
end
x = input('Select benchmark network: ') + 2;

Benchmark = [Allfolders(x).name];
clear Allfolders;

%% Create Labels MNF and run detection algorithm
% Timestamps
t1 = datetime(2017,1,1,0,0,0);
t2 = datetime(2017,12,31,23,30,0);
timeStamps = t1:minutes(30):t2;

dirName = '.\Detection Algorithms\';
AllfoldersLabel = dir(dirName);
fprintf('\nDetection algorithms:\n');
for i=3:length(AllfoldersLabel) % ignore '.', '..'
    fprintf([num2str(i-2),'. ', AllfoldersLabel(i).name, '\n\n']);
end
x = input('Select detection algorithm to simulate: ') + 2;
algorithmSelected = AllfoldersLabel(x).name;
clear AllfoldersLabel;

ScNum = input(['Enter number of scenarios to apply algorithm (1-',num2str(10),'): ']);

dirName = '.\Detection Algorithm Results\';
AllfoldersRes = dir(dirName);
overwriteFolder = 0;
ovwriteinp = 1;
r='Results_';
for i=3:length(AllfoldersRes) % ignore '.', '..'
    chfolder = find(strcmpi(AllfoldersRes(i).name, {[r,'MNF'], [r,'RAND'], [r,'NULL']}));
    if ~isempty(chfolder) && strcmpi([r,algorithmSelected], AllfoldersRes(i).name)
        ovwriteinp = input(['Do you want overwrite labels for ', algorithmSelected,'(yes=1/no=0):']);
        if chfolder==1 && ovwriteinp==1
            gamma = input('Select MNF threshold: ');
        end
        overwriteFolder = 1;
    end
end

% Get all paths from zip file
iszip=0;
BendirName = [pwd,'\Benchmarks\', Benchmark];
if ~isempty(strfind(Benchmark, '.zip'))
    iszip=1;
    [filepaths, file_charpaths, zipFile, streamCopier] = getPathsZip(BendirName);
    Benchmark = Benchmark(1:end-4);
end

% Get results path
respath = [pwd, '\Detection Algorithm Results\Results_',algorithmSelected,'\',Benchmark];
if exist(respath, 'dir')~=7
    mkdir(respath)
end   

% Run create labels
if ovwriteinp==1
    switch algorithmSelected
        case 'MNF' 
            if iszip
                createLabelsMNF(ScNum, respath, timeStamps,...
                    BendirName, iszip, gamma, filepaths, file_charpaths, zipFile, streamCopier);
            else
                createLabelsMNF(ScNum, respath, timeStamps, BendirName, iszip, gamma);
            end
        case 'RAND'
            createLabelsRAND(ScNum, respath, timeStamps);
        case 'NULL'
            createLabelsNULL(ScNum, respath, timeStamps);
    end
elseif ovwriteinp==0
    % skip
else
    disp('Select yes or no.');
    return;
end

%% Scoring algorithm
lblben=NaN(ScNum,length(timeStamps));
lblalg=NaN(ScNum,length(timeStamps));
if ~iszip
    for i=1:ScNum
        strn = num2str(i);
        disp(['Get Labels Bench: Scenario-', strn]);
        filename=[pwd,'\Benchmarks\', Benchmark, '\Scenario-',strn,'\Labels.csv'];
        lblben(i,:)=csvread(filename,1,1);

        disp(['Get Labels Results ',algorithmSelected,': Scenario-', strn]);
        scPath = [respath, '\Scenario-',strn];
        lblalg(i,:)=csvread([scPath,'\Labels.csv'],1,1);
    end  
else

    tempPath = [pwd, '/Benchmarks/Temp/'];
    for i=1:ScNum
        strn = num2str(i);
        ind=strfind(file_charpaths,['Scenario-',strn,'/Labels.csv']);
        ind= ~cellfun(@isempty,ind);
        filepath = filepaths{ind};
    
        disp(['Get Labels Bench: Scenario-', strn]);
        fileInputStream = zipFile.getInputStream(filepath);
        file_bench_path = fileparts(char(filepath));
        foldername = [tempPath, file_bench_path];
        try
            if exist(foldername, 'dir')~=7  
                mkdir(foldername);
            end
        catch
        end
        filename = [tempPath, char(filepath)];
        fileOutputStream = java.io.FileOutputStream(java.io.File([tempPath, char(filepath)]));
        % Extract the entry via the output stream.
        streamCopier.copyStream(fileInputStream, fileOutputStream);
        fileOutputStream.close;
        lblben(i,:)=csvread(filename,1,1);
        
        disp(['Get Labels Results ',algorithmSelected,': Scenario-', strn]);
        scPath = [respath, '\Scenario-',strn];
        lblalg(i,:)=csvread([scPath,'\Labels.csv'],1,1);
    end
    rmdir(fullfile(tempPath), 's')
    % Close the output stream.
    zipFile.close()
    clear filepaths file_charpaths ind timeStamps
end
    
scoring_algorithm(ScNum, lblben, lblalg) 

%% Clear all
clear lblben lblalg; 