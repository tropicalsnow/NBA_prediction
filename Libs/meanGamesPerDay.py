import xlrd
import numpy as np


def meanGamesPerDay(SeasonsList):

    sz=len(SeasonsList)

    gamesPerDay_Array=[]

    for i in range(sz):
        filename='../Data/MarketData_'+str(SeasonsList[i]-1)+"-"+str(SeasonsList[i])[2:4]+'.xlsx'  

        workbook = xlrd.open_workbook(filename, on_demand=True)
        worksheet = workbook.sheet_by_index(0)
    
        games_sz= len(worksheet.col_values(0))-2

        start_row=2 #after the headers where the data starts from

        gamesPerDay=1
        j=start_row
        while j<games_sz+2:

            dateA= str(worksheet.cell(j, 2).value) #get date

            for k in range(1,games_sz-j+2):
                
                dateB= str(worksheet.cell(j+k, 2).value) #get date
                
                
                if dateA==dateB:
                    gamesPerDay=gamesPerDay+1
                else:
                    gamesPerDay_Array.append(gamesPerDay)    
                    gamesPerDay=1
                    break
            j=j+k

        gamesPerDay_Array.append(gamesPerDay)  


    mu = np.mean(gamesPerDay_Array)
    sigma = np.std(gamesPerDay_Array)
    mn = np.min(gamesPerDay_Array)
    mx = np.max(gamesPerDay_Array)

    return mu, sigma, mn, mx

SeasonsList=[2016,2017, 2018, 2019, 2020]

mu, sigma, mn, mx = meanGamesPerDay(SeasonsList)

print(mu, sigma, mn, mx)



