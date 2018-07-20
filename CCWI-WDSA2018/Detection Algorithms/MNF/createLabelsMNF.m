function createLabelsMNF(ScNum, respath, timeStamps, BendirName, iszip, gamma, varargin)

    %% Create labels for MNF
    LScFlows=NaN(ScNum,length(timeStamps));
    if ~iszip
        for i=1:ScNum
            strn = num2str(i);
            disp(['Get Flows Bench: Scenario-', strn]);
            filename=[BendirName, '\Scenario-',strn,'\Flows\Link_1.csv'];
            LScFlows(i,:)=csvread(filename,1,1);
        end
    else
        filepaths = varargin{1};
        file_charpaths = varargin{2};
        zipFile = varargin{3};
        streamCopier = varargin{4};
        
        tempPath = [pwd, '/Benchmarks/Temp/'];
        for i=1:ScNum
            strn = num2str(i);
            ind=strfind(file_charpaths,['Scenario-',strn,'/Flows/Link_1.csv']);
            ind= ~cellfun(@isempty,ind);
            filepath = filepaths{ind};

            disp(['Get Flows Bench: Scenario-', strn]);
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
            LScFlows(i,:)=csvread(filename,1,1);
            try
                rmdir(fullfile(tempPath), 's')
            catch
            end
        end
    end
            
    LabelsMNF=NaN(ScNum,length(timeStamps));
    for i = 1:ScNum
        strn = num2str(i); 
        [Labels_Sc, LabelsMNF(i,:)]  = algorithmMNF(LScFlows(i,:), gamma, timeStamps);
        disp(['Create Labels MNF: Scenario-', strn]);
        scPath = [respath, '\Scenario-',strn,'\'];
        if exist(scPath, 'dir')~=7
            mkdir(scPath)
        end
        f = fopen([scPath,'Labels.csv'], 'w');
        fprintf(f, 'Timestamp, Value\n');
        fprintf(f, '%s\n', Labels_Sc{:});
        fclose('all'); 
    end
    fclose('all'); 
    clear Labels_Sc LabelsMNF LScFlows timeStamps
    
end
