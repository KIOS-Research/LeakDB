function createLabelsNULL(ScNum, respath, timeStamps)

    % Create Labels Results NULL 
    allValues = [datestr(timeStamps, 'yyyy-mm-dd HH:MM') repmat(', 0',[length(timeStamps) 1])];
    allValues = cellstr(allValues);

    for i = 1: ScNum
        strn = num2str(i);
        disp(['Create Labels NULL: Scenario-',strn]);
        scPath = [respath, '\Scenario-',strn,'\'];
        if exist(scPath, 'dir')~=7
            mkdir(scPath)
        end
        f = fopen([scPath,'Labels.csv'], 'w');
        fprintf(f, 'Timestamp, Value\n');
        fprintf(f, '%s\n', allValues{:});
        fclose(f);
    end
    fclose('all');
    clear timeStamps allValues
    
end