import xlrd
import numpy as np
import matplotlib.pyplot as plt 

from scipy.optimize import curve_fit


def Parse_Data_File(hist_worksheet):

    num_of_games=len(hist_worksheet.col_values(0))-2

    Results=[]
    Probs=[]
    Bets=[]
    Outcome=[]
    Score=[]

    #Parse first data file
    for i in  range(num_of_games):

        #read in results [Away=1, Home=2]
        Results.append(hist_worksheet.cell(i+2, 3).value )

        #read in our Bets
        Bets.append(hist_worksheet.cell(i+2, 4).value )

        #read in Probs
        Probs.append(hist_worksheet.cell(i+2, 5).value )

        #Calculate outcome. [1=Correct, 0=Wrong]
        if Bets[i]==Results[i]:
            Outcome.append(1)
        else:
            Outcome.append(0)

    
        Score.append(1-np.power(Probs[i]/100-Outcome[i],2) ) #1-Brier
        #Score.append(  Outcome[i] * np.log(Probs[i]/100) + (1-Outcome[i]) *np.log(1-Probs[i]/100))  # Logarithm


    return Probs, Outcome, Score, num_of_games


def OrganiseBins(Probs, Outcome, Score, num_of_games):

    #Organise the binning of the probabilities
    Bin1=[]
    Bin1_Out=[]
    Bin1_Score=[]
    
    Bin2=[]
    Bin2_Out=[]
    Bin2_Score=[]

    Bin3=[]
    Bin3_Out=[]
    Bin3_Score=[]

    Bin4=[]
    Bin4_Out=[]
    Bin4_Score=[]
    
    Bin5=[]
    Bin5_Out=[]
    Bin5_Score=[]
    
    Bin6=[]
    Bin6_Out=[]
    Bin6_Score=[]

    Bin7=[]
    Bin7_Out=[]
    Bin7_Score=[]
    
    Bin8=[]
    Bin8_Out=[]
    Bin8_Score=[]
    
    Bin9=[]
    Bin9_Out=[]
    Bin9_Score=[]

    Bin10=[]
    Bin10_Out=[]
    Bin10_Score=[]

    for i in  range(num_of_games):

        #Bin 1: 50-55
        if Probs[i]>=50 and Probs[i]<=55:
            Bin1.append(Probs[i])
            Bin1_Out.append(Outcome[i])
            Bin1_Score.append(Score[i])

        #Bin 2: 56-60
        if Probs[i]>=56 and Probs[i]<=60:
            Bin2.append(Probs[i])
            Bin2_Out.append(Outcome[i])
            Bin2_Score.append(Score[i])


        #Bin 3: 61-65
        if Probs[i]>=61 and Probs[i]<=65:
            Bin3.append(Probs[i])
            Bin3_Out.append(Outcome[i])
            Bin3_Score.append(Score[i])

        #Bin 4: 66-70
        if Probs[i]>=66 and Probs[i]<=70:
            Bin4.append(Probs[i])
            Bin4_Out.append(Outcome[i])
            Bin4_Score.append(Score[i])

        #Bin 5: 71-75
        if Probs[i]>=71 and Probs[i]<=75:
            Bin5.append(Probs[i])
            Bin5_Out.append(Outcome[i])
            Bin5_Score.append(Score[i])

        #Bin 6: 76-80
        if Probs[i]>=76 and Probs[i]<=80:
            Bin6.append(Probs[i])
            Bin6_Out.append(Outcome[i])
            Bin6_Score.append(Score[i])


        #Bin 7: 81-85
        if Probs[i]>=81 and Probs[i]<=85:
            Bin7.append(Probs[i])
            Bin7_Out.append(Outcome[i])
            Bin7_Score.append(Score[i])


        #Bin 8: 86-90
        if Probs[i]>=86 and Probs[i]<=90:
            Bin8.append(Probs[i])
            Bin8_Out.append(Outcome[i])
            Bin8_Score.append(Score[i])

        #Bin 9: 91-95
        if Probs[i]>=91 and Probs[i]<=95:
            Bin9.append(Probs[i])
            Bin9_Out.append(Outcome[i])
            Bin9_Score.append(Score[i])

    #Bin 10: 96-100
        if Probs[i]>=96 and Probs[i]<=100:
            Bin10.append(Probs[i])
            Bin10_Out.append(Outcome[i])
            Bin10_Score.append(Score[i])


    meanBin=np.zeros([10])
    meanBin[0] = np.mean(Bin1)
    meanBin[1] = np.mean(Bin2)
    meanBin[2] = np.mean(Bin3)
    meanBin[3] = np.mean(Bin4)
    meanBin[4] = np.mean(Bin5)
    meanBin[5] = np.mean(Bin6)
    meanBin[6] = np.mean(Bin7)
    meanBin[7] = np.mean(Bin8)
    meanBin[8] = np.mean(Bin9)
    meanBin[9] = np.mean(Bin10)


    xBin = np.zeros([10])
    xBin[0]= sum(Bin1_Out)
    xBin[1]= sum(Bin2_Out)
    xBin[2]= sum(Bin3_Out)
    xBin[3]= sum(Bin4_Out)
    xBin[4]= sum(Bin5_Out)
    xBin[5]= sum(Bin6_Out)
    xBin[6]= sum(Bin7_Out)
    xBin[7]= sum(Bin8_Out)
    xBin[8]= sum(Bin9_Out)
    xBin[9]= sum(Bin10_Out)

    nBin = np.zeros([10])
    nBin[0]= len(Bin1_Out)
    nBin[1]= len(Bin2_Out)
    nBin[2]= len(Bin3_Out)
    nBin[3]= len(Bin4_Out)
    nBin[4]= len(Bin5_Out)
    nBin[5]= len(Bin6_Out)
    nBin[6]= len(Bin7_Out)
    nBin[7]= len(Bin8_Out)
    nBin[8]= len(Bin9_Out)
    nBin[9]= len(Bin10_Out)




    meanAcc=np.zeros([10])
    meanAcc[0]= np.mean(Bin1_Out)
    meanAcc[1]= np.mean(Bin2_Out)
    meanAcc[2]= np.mean(Bin3_Out)
    meanAcc[3]= np.mean(Bin4_Out)
    meanAcc[4]= np.mean(Bin5_Out)
    meanAcc[5]= np.mean(Bin6_Out)
    meanAcc[6]= np.mean(Bin7_Out)
    meanAcc[7]= np.mean(Bin8_Out)
    meanAcc[8]= np.mean(Bin9_Out)
    meanAcc[9]= np.mean(Bin10_Out)




    stdAcc=np.zeros([10])
    stdAcc[0]=np.std(Bin1_Out)
    stdAcc[1]=np.std(Bin2_Out)
    stdAcc[2]=np.std(Bin3_Out)
    stdAcc[3]=np.std(Bin4_Out)
    stdAcc[4]=np.std(Bin5_Out)
    stdAcc[5]=np.std(Bin6_Out)
    stdAcc[6]=np.std(Bin7_Out)
    stdAcc[7]=np.std(Bin8_Out)
    stdAcc[8]=np.std(Bin9_Out)
    stdAcc[9]=np.std(Bin10_Out)
    


    meanScore=np.zeros([10])
    meanScore[0]= np.mean(Bin1_Score)
    meanScore[1]= np.mean(Bin2_Score)
    meanScore[2]= np.mean(Bin3_Score)
    meanScore[3]= np.mean(Bin4_Score)
    meanScore[4]= np.mean(Bin5_Score)
    meanScore[5]= np.mean(Bin6_Score)
    meanScore[6]= np.mean(Bin7_Score)
    meanScore[7]= np.mean(Bin8_Score)
    meanScore[8]= np.mean(Bin9_Score)
    meanScore[9]= np.mean(Bin10_Score)

    
    stdScore=np.zeros([10])
    stdScore[0]=np.std(Bin1_Score)
    stdScore[1]=np.std(Bin2_Score)
    stdScore[2]=np.std(Bin3_Score)
    stdScore[3]=np.std(Bin4_Score)
    stdScore[4]=np.std(Bin5_Score)
    stdScore[5]=np.std(Bin6_Score)
    stdScore[6]=np.std(Bin7_Score)
    stdScore[7]=np.std(Bin8_Score)
    stdScore[8]=np.std(Bin9_Score)
    stdScore[9]=np.std(Bin10_Score)
    

    
    return meanBin, meanAcc,xBin, nBin, stdAcc, meanScore, stdScore


def accuracy_binning():

    #Load data files
    seasons=[2016,2017,2018,2019]

    num_of_games=0
    Probs=[]
    Outcome=[]
    Score=[]

    for s in seasons:
        
        hist_workbook = xlrd.open_workbook('./Data/MarketData_'+str(s)+'-'+str(s+1)[2:4] +'.xlsx', on_demand=True)
        hist_worksheet = hist_workbook.sheet_by_index(0)

        Pr, Out, Sc, n_games= Parse_Data_File(hist_worksheet)
    

        num_of_games=num_of_games+n_games
        Probs = np.hstack([Probs,Pr])
        Outcome= np.hstack([Outcome, Out])
        Score =  np.hstack([Score, Sc])

        hist_workbook.release_resources()
    

    #Bin the data
    meanBin, meanAcc,xBin, nBin, stdAcc, meanScore, stdScore = OrganiseBins(Probs, Outcome, Score, num_of_games)



    #Print summary to screen
    for b in range(len(meanBin)):
        print("Bin ", b," Probs: ", meanBin[b]/100,"   Mean Acc.: ",  meanAcc[b], ", Std Acc.: ", stdAcc[b], ", Diff: ",  meanBin[b]/100 -  meanAcc[b]  )
        print("\t\t   Mean Score.: ",  meanScore[b], ", Std Score.: ", stdScore[b])

    #Plot graph
    # plt.subplot(3,1,1)
    # plt.fill_between(meanBin/100,  np.add(meanAcc,stdAcc), np.subtract(meanAcc,stdAcc), color='b', alpha=.5)
    # plt.plot(meanBin/100, meanAcc, marker='o', linestyle='dashed', color='b')
    # plt.plot(meanBin/100, stdAcc, marker='o', linestyle='dashed', color='g')
    # plt.ylabel("Acc & std")

    # plt.subplot(3,1,2)
    # plt.fill_between(meanBin/100,  np.add(meanScore,stdScore), np.subtract(meanScore,stdScore), color='g', alpha=.5)
    # plt.plot(meanBin/100, meanScore, marker='o', linestyle='dashed',)
    # plt.ylabel("1-Brier")

    # plt.subplot(3,1,3)
    plt.figure(100)
    plt.plot(meanBin/100,  meanBin/100 -  meanAcc , marker='o', linestyle='dashed',)
    plt.ylabel("Diff")


    #print("Excel formula (10 bins):  =IF(F3<=55,F3 +0.95,     IF (AND( F3>=56, F3<=60 ), F3 + 3.79 ,  IF( AND(F3>=61,F3<=65 ), F3+ 1.39 , IF(  AND(F3>=66,F3<=70), F3+1.99, IF( AND(F3>=71, F3<=75) , F3+1.529,  IF(  AND(F3>=76, F3<=80) ,   F3+3.74 , IF(   AND(F3>=81,F3<=85), F3-2.98, IF(  AND(F3>=86,F3<=90),  F3-1.59, IF(  AND(F3>=91,F3<=95),  F3-2.63, F3-1.47    ) ) ) ) ) ) ) ) )")



    plt.show()



    return meanAcc, xBin, nBin



accuracy_binning()