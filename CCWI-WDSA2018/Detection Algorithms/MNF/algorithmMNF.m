function [Labels_Sc, Labels_Sc_Final1] = algorithmMNF(LScFlows, gamma, timeStamps)

    %% MNF code
    w=10; % window    
    k = 1:w;
    Labels_Sc=[];

    MNF = min(reshape(LScFlows,48,365));
    for j=(w+1):365
        minMNFW = min(MNF(k));
        e = MNF(j)-minMNFW;
        if e>minMNFW*gamma
            Labels_Sc(j) = 1;
        else
            Labels_Sc(j) = 0;
            k(w+1) = j;
            k(1) = [];
        end
    end
    
    Labels_Sc_Final1 = [];
    j=48;
    for d=1:size(Labels_Sc,2)
        Labels_Sc_Final1(j-47:j,1)=Labels_Sc(d);
        j = j+48;
    end
    
    clear Labels_Sc
    Labels_Sc = [datestr(timeStamps, 'yyyy-mm-dd HH:MM') repmat(', ',length(timeStamps),1) num2str(repmat(Labels_Sc_Final1, 1))];
    Labels_Sc = cellstr(Labels_Sc);
    
end
