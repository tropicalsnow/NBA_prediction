#TODO: Verify on game results


import json
from pprint import pprint
from datetime import datetime
from dateutil import tz
import xlrd
import xlsxwriter
import os, os.path
import random
import subprocess
import codecs, sys
 
from TeamsList import Teams, getTeam_by_Short, getTeam_by_Name, getTeam_by_partial_ANY
 
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)  #For printing out unicode in Windows console


def unzipAll(fulldir):

    _, dirs, _ = next(os.walk(fulldir))
    for dr in dirs:
        print(dr)
        output= subprocess.call(["C:/Program Files/7-zip/7z.exe", "e", fulldir+dr+"/*.bz2", "-o"+fulldir+dr,"-y"])
        if output==0:
            _, _, files = next(os.walk(fulldir+dr))
            for fl in files:
                if fl.endswith(".bz2"):
                    os.remove(fulldir+dr+"/"+fl)
  



from_zone = tz.gettz('GMT')
to_zone = tz.gettz('EST')



JSON_dir="C:/Users/Vasileios/Downloads/C_/data/xds/historic/BASIC/"
history_file="Data/Games_2015-16.xlsx"
output_file="Data/MarketData_2015-16.xlsx"





unzipAll(JSON_dir)

  
 

 
#Parse game history file
workbook = xlrd.open_workbook(history_file, on_demand=True)
worksheet = workbook.sheet_by_index(0)
ngames=len(worksheet.col_values(0))-2

 
#Create output file
out_workbook = xlsxwriter.Workbook(output_file)
out_worksheet = out_workbook.add_worksheet()
#Write header
out_worksheet.write(0,0,"Away")
out_worksheet.write(0,1,"Home")
out_worksheet.write(0,2,"Date")
out_worksheet.write(0,3,"Result")
out_worksheet.write(0,4,"Our prediction")
out_worksheet.write(0,5,"Our probs")
out_worksheet.write(0,6,"BETFAIR odds")
out_worksheet.write(0,8,"BETFAIR predictions")
out_worksheet.write(0,9,"BETFAIR probs")
out_worksheet.write(0,11,"Carmelo probs")
out_worksheet.write(0,11,"Carmelo predictions")
 
 



for i in range(ngames):

    print(i)
 
    away_team_Short = worksheet.cell(i+2, 0).value
    atm=getTeam_by_Short(away_team_Short)
    away_team=atm.name
    
    home_team_Short = worksheet.cell(i+2, 1).value
    htm=getTeam_by_Short(home_team_Short)
    home_team=htm.name
    
    dateEST=  datetime.strptime(worksheet.cell(i+2, 6).value, '%m/%d/%y')
    
    game_result= worksheet.cell(i+2, 5).value







    #Write to output file
    out_worksheet.write(i+2, 0, away_team_Short) #Away team
    out_worksheet.write(i+2, 1, home_team_Short) #Home team
    date_string= str(dateEST.strftime("%m")+"/"+dateEST.strftime("%d")+"/"+dateEST.strftime("%y"))
    out_worksheet.write(i+2, 2, date_string) #Date (EST)
    out_worksheet.write(i+2, 3, game_result) #Game result



    #Iterate over all JSON files
    _, dirs, _ = next(os.walk(JSON_dir))
    for d in dirs:

        timestamp=0
        inplay_timestamp=random.getrandbits(128)

        
        _, _, files = next(os.walk(JSON_dir+d))
        for f in files:   

            # print(JSON_dir+d+"/"+f)
 
            away_team_ID=None
            home_team_ID=None
            away_team_Odds=None
            home_team_Odds=None
            dateGMT=None
            inplay_away_team_Odds=None
            inplay_home_team_Odds=None

            skipFlag=0
            delFile=0
            inPlay_flag=False
             

            #Parse Betfair JSON history file
            for line in open(JSON_dir+d+"/"+f, encoding="utf-8"):
            
                
                data = json.loads(line)






                #Do basic tests on the JSON file
                if 'marketDefinition' in data['mc'][0]:
                    #Make sure its a moneyline and match_odds market
                    if data['mc'][0]['marketDefinition']['name'] != "Moneyline"  or  data['mc'][0]['marketDefinition']['marketType'] != "MATCH_ODDS":
                        skipFlag=1
                        delFile=1 # Flag the file for deletion
                        break                    
                    #Only consider data from international regulators
                    if 'regulators' in data['mc'][0]['marketDefinition']:
                        if data['mc'][0]['marketDefinition']['regulators'][0] != "MR_INT":
                            skipFlag=1
                            delFile=1 # Flag the file for deletion
                            break
                    
  


                if away_team_ID is None or home_team_ID is None:


                    #Skip AND mark for deletion any files that do not have valid NBA teams inside
                    outA=getTeam_by_partial_ANY(data['mc'][0]['marketDefinition']['runners'][0]['name'])
                    outH=getTeam_by_partial_ANY(data['mc'][0]['marketDefinition']['runners'][1]['name'])
                    if outA==None or outH==None:
                        skipFlag=1
                        delFile=1 # Flag the file for deletion
                        print("DELETING FILE: ",data['mc'][0]['marketDefinition']['runners'][0]['name'],data['mc'][0]['marketDefinition']['runners'][1]['name'],JSON_dir+d+"/"+f) 
                        break


                    #Skip file if it does not have AWAY team inside
                    # if away_team == data['mc'][0]['marketDefinition']['runners'][0]['name']:
                    if away_team == getTeam_by_partial_ANY(data['mc'][0]['marketDefinition']['runners'][0]['name']).name:
                        away_team_ID= data['mc'][0]['marketDefinition']['runners'][0]['id']
                    else:
                        skipFlag=1
                        break
           
                    #Skip file if it does not have HOME team inside
                    if home_team == getTeam_by_partial_ANY(data['mc'][0]['marketDefinition']['runners'][1]['name']).name:
                        home_team_ID= data['mc'][0]['marketDefinition']['runners'][1]['id']  
                    else:
                        skipFlag=1
                        break




                #Get date (GMT) and convert to EST
                if 'marketDefinition' in data['mc'][0]:
                    dateGMT = data['mc'][0]['marketDefinition']['openDate'][0:16]
                    dateGMT =  datetime.strptime(dateGMT, '%Y-%m-%dT%H:%M')
                    dateGMT = dateGMT.replace(tzinfo=from_zone)
                    dateGMT = dateGMT.astimezone(to_zone)

            
                
                if 'marketDefinition' in data['mc'][0]:
                    inPlay_flag = data['mc'][0]['marketDefinition']['inPlay']               
                   



                if inPlay_flag==False: #Out of play

                    if data['pt']>timestamp:  #Only consider the LATEST timestamp data BEFORE the game starts
                        timestamp= data['pt']

                        odds=[]
                        if 'rc' in data['mc'][0]:
                            odds=data['mc'][0]['rc']
                            for j in range(len(odds)):
                                if odds[j]['id'] == away_team_ID:
                                    away_team_Odds=odds[j]['ltp']
                                elif odds[j]['id'] == home_team_ID:
                                    home_team_Odds=odds[j]['ltp']


                else:       #In play

                    #Capture initial inplay odds in case out-of-play odds do not exist
                    if data['pt']<inplay_timestamp:  #Only consider the EARLIEST timestamp data AFTER the game starts
                        inplay_timestamp= data['pt']  
                        
                        inplay_odds=[]
                        if 'rc' in data['mc'][0]:
                            inplay_odds=data['mc'][0]['rc']
                            for j in range(len(inplay_odds)):
                                if inplay_odds[j]['id'] == away_team_ID:
                                    inplay_away_team_Odds=inplay_odds[j]['ltp']
                                elif inplay_odds[j]['id'] == home_team_ID:
                                    inplay_home_team_Odds=inplay_odds[j]['ltp']
                    


            if skipFlag:
                if delFile:
                    os.remove(JSON_dir+d+"/"+f)
                # break
            else:


                #Check that the dates match    
                if dateGMT.year == dateEST.year and dateGMT.month == dateEST.month and dateGMT.day == dateEST.day :
 
                    if     away_team_Odds is not None and home_team_Odds is not None:
                        #Write to output file
                        out_worksheet.write(i+2, 6, float(away_team_Odds)) #Away team Betfair odds
                        out_worksheet.write(i+2, 7, float(home_team_Odds)) #Home team Betfair odds

                        if away_team_Odds>home_team_Odds:
                            out_worksheet.write(i+2, 8, 2)
                        else:
                            out_worksheet.write(i+2, 8, 1)

                        out_worksheet.write(i+2, 9, float(1/away_team_Odds)*100)  #Away team Betfair implied probs
                        out_worksheet.write(i+2, 10, float(1/home_team_Odds)*100) #Home team Betfair implied probs
                        
                        out_worksheet.write(i+2,12, JSON_dir+d+"/"+f)  #history file with the data
                        
                        print(away_team, "-",home_team, "|",dateEST, "-", dateGMT,  "|",away_team_Odds,"-",home_team_Odds)
                        print(JSON_dir+d+"/"+f)

                    elif inplay_away_team_Odds is not None and inplay_home_team_Odds is not None:
                        #input the first inPlay odds instead
                        
                        #Write to output file
                        out_worksheet.write(i+2, 6, float(inplay_away_team_Odds)) #Away team Betfair odds
                        out_worksheet.write(i+2, 7, float(inplay_home_team_Odds)) #Home team Betfair odds

                        if inplay_away_team_Odds>inplay_home_team_Odds:
                            out_worksheet.write(i+2, 8, 2)
                        else:
                            out_worksheet.write(i+2, 8, 1)

                        out_worksheet.write(i+2, 9, float(1/inplay_away_team_Odds)*100)  #Away team Betfair implied probs
                        out_worksheet.write(i+2, 10, float(1/inplay_home_team_Odds)*100) #Home team Betfair implied probs
                        
                        out_worksheet.write(i+2,12, JSON_dir+d+"/"+f)  #history file with the data
                        
                        print(away_team, "-",home_team, "|",dateEST, "-", dateGMT,  "|",inplay_away_team_Odds,"-",inplay_home_team_Odds)
                        print(JSON_dir+d+"/"+f)
    


out_workbook.close()



            