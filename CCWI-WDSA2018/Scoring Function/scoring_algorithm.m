function scoring_algorithm(ScNum, lblben, lblalg) 

    %% TP TN FP FN
    TPall = ((lblben==1) & (lblalg==1));
    TP=sum(TPall,2);

    TNall = ((lblben==0) & (lblalg==0));
    TN=sum(TNall,2);


    FPall = ((lblben==0) & (lblalg==1));
    FP=sum(FPall,2);

    FNall = ((lblben==1) & (lblalg==0));
    FN=sum(FNall,2);

    ConfMat = [TP TN FP FN];

    %% F1 score
    TP = length(find(lblben==1 & lblalg==1));
    FP = length(find(lblben==0 & lblalg==1));
    FN = length(find(lblben==1 & lblalg==0));
    F1 = 2*TP./(2*TP+FP+FN)*100;
    disp(['Score F1: ', num2str(F1)]);

    %% Matthews correlation coeffient
    MCC = (TP.*TN-FP.*FN) ./ sqrt((TP+FP).*(TP+FN).*(TN+FP).*(TN+FN));

    %% True Positive Rate
    TPplusFN = length(find(lblben==1));
    TP = length(find(lblben==1 & lblben==lblalg));
    STPR = TP/TPplusFN*100;
    disp(['Score STPR: ', num2str(STPR)]);

    %% True Negative Rate
    FPplusTN = length(find(lblben==0));
    TN = length(find(lblben==0 & lblben==lblalg));
    STNR = TN/FPplusTN*100;
    disp(['Score STNR: ', num2str(STNR)]);

    %% Early detection score
    tw_ex=10; % extra time for scoring window
    max_win = length(lblben(1,:)); % maximum window reach
    SEDthr=0.75;
    for i=1:ScNum
        faultStartTimes = find(diff(lblben(i,:))==1) + 1; %find fault times
        faultEndTimes = find(diff(lblben(i,:))==-1);
        sf=[];sfid=[];
        for j = 1:length(faultStartTimes)
            tf=faultStartTimes(j);
            if (faultEndTimes(j)+tw_ex)>max_win; tw_ex=max_win-faultEndTimes(j);end
            tw = faultEndTimes(j)-faultStartTimes(j)+tw_ex;

            x=tf:tf+tw;
            DW = lblalg(i,x); % Detection Window

            Dt=min(find(DW==1))-1; %first detection time
            if (sum(DW(Dt+1:end))/length(DW(Dt+1:end)))>SEDthr

                Dt=Dt;
            else
                Dt=[];
            end

            if isempty(Dt)
                sf(j)=0; %fault not detected
            else
                sf(j) = 2./(1+exp((5/tw).*Dt)); %score for fault 
            end
            sfid(j) = 1; %ideal score for fault detection   
        end
        s(i) = sum(sf); %score for scenario
        sid(i) = sum(sfid); %ideal score for scenario
    end
    SED = sum(s)/sum(sid)*100; %total score of algorithm
    disp(['Score SED: ', num2str(SED)]);

    clear lblben lblalg timeSteps
    
end
