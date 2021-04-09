import xlrd
import os, os.path
from datetime import datetime
from xlutils.copy import copy
import numpy as np


history_file="./Data/Market_data/MarketData_2014-15.xlsx"
CARMELO_history_file="./Data/Experts_data/CARMELO_data_2009-2019.xlsx"


#Parse history files
HISTORY_workbook = xlrd.open_workbook(history_file, on_demand=True)
HISTORY_worksheet = HISTORY_workbook.sheet_by_index(0)

wb = copy(HISTORY_workbook) # a writable copy (I can't read values out of this, only write to it)
w_sheet = wb.get_sheet(0) # the sheet to write to within the writable copy


history_games=len(HISTORY_worksheet.col_values(0))-2





CARMELO_workbook = xlrd.open_workbook(CARMELO_history_file, on_demand=True)
CARMELO_worksheet = CARMELO_workbook.sheet_by_index(0)
carmelo_history_games=len(CARMELO_worksheet.col_values(0))-2


#Loop over history data
for i in range(history_games):

    #Get game info
    away_team_Short = HISTORY_worksheet.cell(i+2, 0).value
    home_team_Short = HISTORY_worksheet.cell(i+2, 1).value
    date            = HISTORY_worksheet.cell(i+2, 2).value
    result          = int(HISTORY_worksheet.cell(i+2, 3).value)


    found_flag=False

    print(i)


    #Loop over CARMELO history data
    for j in range(carmelo_history_games):

        CARMELO_away_team_Short = CARMELO_worksheet.cell(j+1, 5).value
        #Fix discrepancies in short names for AWAY teams between NBA.com and FIVETHIRTYEIGHT 
        if CARMELO_away_team_Short=="BRK":
            CARMELO_away_team_Short="BKN"
        if CARMELO_away_team_Short=="CHO":
            CARMELO_away_team_Short="CHA"            
        if CARMELO_away_team_Short=="PHO":
            CARMELO_away_team_Short="PHX"
        
 
        CARMELO_home_team_Short = CARMELO_worksheet.cell(j+1, 4).value
        #Fix discrepancies in short names for HOME teams between NBA.com and FIVETHIRTYEIGHT 
        if CARMELO_home_team_Short=="BRK":
            CARMELO_home_team_Short="BKN"
        if CARMELO_home_team_Short=="CHO":
            CARMELO_home_team_Short="CHA"            
        if CARMELO_home_team_Short=="PHO":
            CARMELO_home_team_Short="PHX"    


        dt  =   datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(CARMELO_worksheet.cell(j+1, 0).value) - 2)
        CARMELO_date= str(dt.month).zfill(2) +"/"+str(dt.day).zfill(2) +"/"+str(dt.year)[2:4]
 
        

        CARMELO_HOME_prob       = CARMELO_worksheet.cell(j+1, 16).value or 0
        CARMELO_AWAY_prob       = CARMELO_worksheet.cell(j+1, 17).value or 0

        CARMELO_HOME_score       = CARMELO_worksheet.cell(j+1, 22).value
        CARMELO_AWAY_score       = CARMELO_worksheet.cell(j+1, 23).value
        if CARMELO_AWAY_score>CARMELO_HOME_score:
            CARMELO_result=1
        else:
            CARMELO_result=2
 


        #Compare historical data with CARMELO data
        if (away_team_Short==CARMELO_away_team_Short) and (home_team_Short==CARMELO_home_team_Short) and (date==CARMELO_date) and (result==CARMELO_result):
            
            if CARMELO_AWAY_prob==0 and CARMELO_HOME_prob==0:
                w_sheet.write(2+i, 11, 0) #CARMELO Predictions
            else:
                w_sheet.write(2+i, 11, int(np.argmax([CARMELO_AWAY_prob, CARMELO_HOME_prob])+1)) #CARMELO Predictions
            w_sheet.write(2+i, 12, float(np.max([CARMELO_AWAY_prob, CARMELO_HOME_prob])*100)) #CARMELO Probs

            found_flag=True
            break

    
    if found_flag is False:
        print(away_team_Short, home_team_Short,  date, result)
        raise Exception('Historical entry not found in CARMELO data')  


wb.save(history_file)  