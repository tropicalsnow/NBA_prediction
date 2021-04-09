#Manual datastruct of team names and web IDs

class structtype():
    pass



teams_sz=30
Teams = [ structtype() for i in range(teams_sz)]

Teams[0].name='Boston Celtics'         
Teams[0].name_old='Boston Celtics'       
Teams[0].name_old2='Boston Celtics'       
Teams[0].short='BOS'   
Teams[0].ID=1610612738

Teams[1].name='Brooklyn Nets'
Teams[1].name_old='New Jersey Nets'
Teams[1].name_old2='New Jersey Nets'
Teams[1].short='BKN'
Teams[1].ID=1610612751

Teams[2].name='New York Knicks'
Teams[2].name_old='New York Knicks'
Teams[2].name_old2='New York Knicks'
Teams[2].short='NYK'
Teams[2].ID=1610612752

Teams[3].name='Philadelphia 76ers'  
Teams[3].name_old='Philadelphia 76ers'
Teams[3].name_old2='Philadelphia 76ers'
Teams[3].short='PHI'    
Teams[3].ID=1610612755

Teams[4].name='Toronto Raptors' 
Teams[4].name_old='Toronto Raptors' 
Teams[4].name_old2='Toronto Raptors' 
Teams[4].short='TOR'   
Teams[4].ID=1610612761

Teams[5].name='Chicago Bulls'  
Teams[5].name_old='Chicago Bulls'  
Teams[5].name_old2='Chicago Bulls'  
Teams[5].short='CHI'    
Teams[5].ID=1610612741

Teams[6].name='Miami Heat'       
Teams[6].name_old='Miami Heat'
Teams[6].name_old2='Miami Heat'
Teams[6].short='MIA'    
Teams[6].ID=1610612748

Teams[7].name='Milwaukee Bucks'  
Teams[7].name_old='Milwaukee Bucks'  
Teams[7].name_old2='Milwaukee Bucks'  
Teams[7].short='MIL'  
Teams[7].ID=1610612749

Teams[8].name='New Orleans Pelicans' 
Teams[8].name_old='New Orleans Hornets' 
Teams[8].name_old2='New Orleans/Oklahoma City Hornets' 
Teams[8].short='NOP'  
Teams[8].ID=1610612740

Teams[9].name='Denver Nuggets'        
Teams[9].name_old='Denver Nuggets'
Teams[9].name_old2='Denver Nuggets'
Teams[9].short='DEN'   
Teams[9].ID=1610612743

Teams[10].name='Golden State Warriors'
Teams[10].name_old='Golden State Warriors'
Teams[10].name_old2='Golden State Warriors'
Teams[10].short='GSW'
Teams[10].ID=1610612744

Teams[11].name='Sacramento Kings'   
Teams[11].name_old='Sacramento Kings'
Teams[11].name_old2='Sacramento Kings'
Teams[11].short='SAC'    
Teams[11].ID=1610612758

Teams[12].name='Los Angeles Lakers'  
Teams[12].name_old='LA Lakers'  
Teams[12].name_old2='L.A. Lakers'  
Teams[12].short='LAL'    
Teams[12].ID=1610612747

Teams[13].name='Dallas Mavericks'  
Teams[13].name_old='Dallas Mavericks'  
Teams[13].name_old2='Dallas Mavericks'  
Teams[13].short='DAL'  
Teams[13].ID=1610612742

Teams[14].name='Atlanta Hawks'       
Teams[14].name_old='Atlanta Hawks'       
Teams[14].name_old2='Atlanta Hawks'       
Teams[14].short='ATL'   
Teams[14].ID=1610612737

Teams[15].name='Cleveland Cavaliers'
Teams[15].name_old='Cleveland Cavaliers'
Teams[15].name_old2='Cleveland Cavaliers'
Teams[15].short='CLE'    
Teams[15].ID=1610612739

Teams[16].name='Washington Wizards'   
Teams[16].name_old='Washington Bullets'   
Teams[16].name_old2='Washington Bullets'   
Teams[16].short='WAS'    
Teams[16].ID=1610612764

Teams[17].name='Charlotte Hornets' 
Teams[17].name_old='Charlotte Bobcats'
Teams[17].name_old2='Charlotte Bobcats'
Teams[17].short='CHA' 
Teams[17].ID=1610612766

Teams[18].name='Orlando Magic'    
Teams[18].name_old='Orlando Magic'  
Teams[18].name_old2='Orlando Magic'  
Teams[18].short='ORL'   
Teams[18].ID=1610612753

Teams[19].name='Utah Jazz'    
Teams[19].name_old='Utah Jazz'    
Teams[19].name_old2='Utah Jazz'
Teams[19].short='UTA'  
Teams[19].ID=1610612762

Teams[20].name='Indiana Pacers'   
Teams[20].name_old='Indiana Pacers'   
Teams[20].name_old2='Indiana Pacers'   
Teams[20].short='IND'  
Teams[20].ID=1610612754

Teams[21].name='Detroit Pistons'    
Teams[21].name_old='Detroit Pistons'    
Teams[21].name_old2='Detroit Pistons'    
Teams[21].short='DET'   
Teams[21].ID=1610612765

Teams[22].name='San Antonio Spurs'  
Teams[22].name_old='San Antonio Spurs'  
Teams[22].name_old2='San Antonio Spurs' 
Teams[22].short='SAS'   
Teams[22].ID=1610612759

Teams[23].name='Portland Trail Blazers'
Teams[23].name_old='Portland Trail Blazers'
Teams[23].name_old2='Portland Trail Blazers'
Teams[23].short='POR'   
Teams[23].ID=1610612757

Teams[24].name='Oklahoma City Thunder'
Teams[24].name_old='Seattle SuperSonics'
Teams[24].name_old2='Seattle SuperSonics'
Teams[24].short='OKC'  
Teams[24].ID=1610612760

Teams[25].name='Los Angeles Clippers'    
Teams[25].name_old='LA Clippers'    
Teams[25].name_old2='L.A. Clippers'   
Teams[25].short='LAC'   
Teams[25].ID=1610612746

Teams[26].name='Phoenix Suns'    
Teams[26].name_old='Phoenix Suns'    
Teams[26].name_old2='Phoenix Suns'    
Teams[26].short='PHX'   
Teams[26].ID=1610612756

Teams[27].name='Minnesota Timberwolves'
Teams[27].name_old='Minnesota Timberwolves'
Teams[27].name_old2='Minnesota Timberwolves'
Teams[27].short='MIN' 
Teams[27].ID=1610612750

Teams[28].name='Memphis Grizzlies'  
Teams[28].name_old='Vancouver Grizzlies'  
Teams[28].name_old2='Vancouver Grizzlies'  
Teams[28].short='MEM'  
Teams[28].ID=1610612763

Teams[29].name='Houston Rockets'
Teams[29].name_old='Houston Rockets'
Teams[29].name_old2='Houston Rockets'
Teams[29].short='HOU'       
Teams[29].ID=1610612745




def getTeam_by_Short(short):

    for i in range(teams_sz):

        if short == Teams[i].short:
            return Teams[i]
    return None

def getTeam_by_Name(name):
    for i in range(teams_sz):

        if name == Teams[i].name:
            return Teams[i]
    return None

def getTeam_by_NameOLD(name_old):
    for i in range(teams_sz):

        if name_old == Teams[i].name_old:
            return Teams[i]
    return None

def getTeam_by_ID(id):
    for i in range(teams_sz):

        if int(id) == Teams[i].ID:
            return Teams[i]
    return None   

def getTeam_by_partial_ANY(text):
    for i in range(teams_sz):
        if  text in Teams[i].name or text in Teams[i].name_old or text in Teams[i].name_old2:
            return Teams[i]
    return None


def getTeam_by_partial_Name(text):
    for i in range(teams_sz):
        if  text in Teams[i].name:
            return Teams[i]
    return None


