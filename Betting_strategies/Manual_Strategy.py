
import xlrd, xlsxwriter
from xlutils.copy import copy
import os
import math


def Manual_Strategy(Probs,Market_Odds,  Balance, Accuracy, game_no, Profit ):

    Stakes=[]
    Bets=[]
    Unsettled_Balance=Balance
    if math.isnan(Accuracy):
        Accuracy=1 
    
    #Create/Load manual-betting datafile for training a REGRESSOR later on 
    filename='manual_betting_features.xlsx'
    file_exists=False
    if os.path.isfile(filename):
        workbook = xlrd.open_workbook(filename, on_demand=True)
        worksheet = workbook.sheet_by_index(0)

        wb = copy(workbook) # a writable copy (I can't read values out of this, only write to it)
        w_sheet = wb.get_sheet(0) # the sheet to write to within the writable copy
        start_row= worksheet.nrows
        file_exists=True
    else:
        workbook = xlsxwriter.Workbook(filename)
        w_sheet = workbook.add_worksheet()

        #Add header

        w_sheet.write(0, 0 ,  'Balance') #Balance
        w_sheet.write(0, 1 ,  'Probs Away') #Probs
        w_sheet.write(0, 2 ,  'Probs Home') 
        w_sheet.write(0, 3 ,  'Market Odds Away') #market odds
        w_sheet.write(0, 4 ,  'Market Odds Home') 
        w_sheet.write(0, 5 ,  'Exposure') #Exposure
        w_sheet.write(0, 6 ,  'Day game no') #day game no
        w_sheet.write(0, 7 ,  'Total games in day') #total games in day
        w_sheet.write(0, 8 ,  'Season game no') #Absolute game
        w_sheet.write(0, 9 ,  'Accuracy') #Accuracy
        w_sheet.write(0, 10 ,  'Profit') #Profit

        w_sheet.write(0, 12 ,  'Bet_Side') #Bet side
        w_sheet.write(0, 13,   'Bet Amount') #Bet stake


        start_row=1


    print("Balance: ", Balance)
    for i in range(len(Probs)):
        print("GAME ",i+1, " OUT OF ",len(Probs))
        print("Probablities are (away, home) \t\t %.3f, %.3f" %(Probs[i,0],Probs[i,1]))
        print("Market odds  %.3f, %.3f  (Probs: \t %.3f, %.3f)" %(Market_Odds[i,0], Market_Odds[i,1],1/Market_Odds[i,0], 1/Market_Odds[i,1]))
        print("Day exposure: ", Balance-Unsettled_Balance)
        print("....................................")

        Bet_Side=0
        Bet_Amt=-1
        while Bet_Side !=1 and Bet_Side !=2:
            try:
                Bet_Side = int(input("Choose side, 1 = away, 2 = home:  ") or 0)
            except:
                Bet_Side=0
        while Bet_Amt <0:
            try:
                Bet_Amt = float(input("Choose bet amount:  \n") or 0)
            except:
                Bet_Amt=-1
        
        if Bet_Amt <= Unsettled_Balance:
            Unsettled_Balance = Unsettled_Balance - Bet_Amt

        Stakes.append(Bet_Amt)
        Bets.append(Bet_Side)

        #Write to excel
        w_sheet.write(start_row+i, 0 ,  Balance) #Balance
        w_sheet.write(start_row+i, 1 ,  Probs[i,0]) #Probs
        w_sheet.write(start_row+i, 2 ,  Probs[i,1]) #Probs
        w_sheet.write(start_row+i, 3 ,  Market_Odds[i,0]) #market odds
        w_sheet.write(start_row+i, 4 ,  Market_Odds[i,1]) #market odds
        w_sheet.write(start_row+i, 5 ,  Balance-Unsettled_Balance) #Exposure
        w_sheet.write(start_row+i, 6 ,  i+1) #day game no
        w_sheet.write(start_row+i, 7 ,  len(Probs)) #total games in day
        w_sheet.write(start_row+i, 8 ,  game_no+i+1) #Absolute game
        w_sheet.write(start_row+i, 9 ,  Accuracy) #Accuracy
        w_sheet.write(start_row+i, 10 ,  Profit) #Profit

        w_sheet.write(start_row+i, 12 ,  Bet_Side) #Bet side
        w_sheet.write(start_row+i, 13,   Bet_Amt) #Bet stake


    if file_exists:
        workbook.release_resources()
        wb.save(filename)
    else:
        workbook.close()

      
    return Stakes, Bets