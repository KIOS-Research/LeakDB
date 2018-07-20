function createLabelsRAND(ScNum, respath, timeStamps)

    % Create Labels Results NULL 
    values = randi([0 1], length(timeStamps),1);
    allValues = [datestr(timeStamps, 'yyyy-mm-dd HH:MM') repmat(', ',length(timeStamps),1) num2str(repmat(values, 1))];
    allValues = cellstr(allValues);

    for i = 1: ScNum
        strn = num2str(i);
        disp(['Create Labels RAND: Scenario-',strn]);
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
    clear timeStamps allValues values
    
end