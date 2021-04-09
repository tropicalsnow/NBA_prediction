#USING SQLITE instead of SQLALCHEMY
import sqlite3
import os




class MyDatabase:

    def __init__(self, filename):
        self.dbfile=filename  
        self.conn = sqlite3.connect(self.dbfile)

    def closeConnection(self):
        self.conn.commit()
        self.conn.close()
 
    def create_Games_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Games (game_id TEXT NOT NULL, "
        "Away_Team_id TEXT NOT NULL, " 
        "Home_Team_id TEXT NOT NULL, " 
        "Away_Score INTEGER NOT NULL, " 
        "Home_Score INTEGER NOT NULL, " 
        "Result INTEGER NOT NULL, " 
        "Date TEXT NOT NULL, "

        "PRIMARY KEY(game_id),"
        "FOREIGN KEY(Away_Team_id) REFERENCES Teams(team_id),"
        "FOREIGN KEY(Home_Team_id) REFERENCES Teams(team_id) )")
    
        self.conn.commit()


    def create_Teams_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Teams (team_id TEXT NOT NULL, "
        "team_name TEXT NOT NULL, " 
        "short_name TEXT NOT NULL, "

        "PRIMARY KEY(team_id))")

        self.conn.commit()


    def create_Players_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Players (player_id TEXT NOT NULL, "
        "player_name TEXT NOT NULL, " 
        "age INTEGER, "
        "exp INTEGER, "
        "weight FLOAT, "
        "height FLOAT, "

        "PRIMARY KEY(player_id))")

        self.conn.commit()


    def create_Lineups_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE Lineups (player_id TEXT NOT NULL, "
        "game_id TEXT NOT NULL, " 
        "team_id TEXT NOT NULL, " 

        "FOREIGN KEY(player_id) REFERENCES Players(player_id),"
        "FOREIGN KEY(game_id) REFERENCES Games(game_id),"
        "FOREIGN KEY(team_id) REFERENCES Teams(team_id),"
        "PRIMARY KEY(player_id, game_id, team_id))")
        
        self.conn.commit()


    def create_BoxscoresPlayer_Table(self):
        c = self.conn.cursor()
        c.execute(
        "CREATE TABLE BoxscoresPlayer (game_id TEXT NOT NULL, "
        "player_id TEXT NOT NULL, " 
        
        #TRADITIONAL
        "MIN FLOAT, "
        "FGM  FLOAT, "
        "FGA FLOAT, "
        "FG_PCT FLOAT, "
        "FG3M FLOAT, "
        "FG3A FLOAT, "
        "FG3_PCT FLOAT, "
        "FTM FLOAT, "
        "FTA FLOAT, "
        "FT_PCT FLOAT, "
        "OREB FLOAT, "
        "DREB FLOAT, "
        "REB FLOAT, "
        "AST FLOAT, "
        "STL FLOAT, "
        "BLK FLOAT, "
        "TOV FLOAT, "
        "PF FLOAT, "
        "PTS FLOAT, "
        "PLUS_MINUS FLOAT,"
        #ADVANCED
        "E_OFF_RATING FLOAT, "
        "OFF_RATING FLOAT, "
        "E_DEF_RATING FLOAT, "
        "DEF_RATING FLOAT, "
        "E_NET_RATING FLOAT, "
        "NET_RATING FLOAT, "
        "AST_PCT FLOAT, "
        "AST_TOV FLOAT, "
        "AST_RATIO FLOAT, "
        "OREB_PCT FLOAT, "
        "DREB_PCT FLOAT, "
        "REB_PCT FLOAT, "
        "TOV_PCT FLOAT, "
        "EFG_PCT FLOAT, "
        "TS_PCT FLOAT, "
        "USG_PCT FLOAT, "
        "E_USG_PCT FLOAT, "
        "E_PACE FLOAT, "
        "PACE FLOAT, "
        "PIE FLOAT, "
        #MISC
        "PTS_OFF_TOV FLOAT, "
        "PTS_2ND_CHANCE FLOAT, "
        "PTS_FB FLOAT, "
        "PTS_PAINT FLOAT, "
        "OPP_PTS_OFF_TOV FLOAT, "
        "OPP_PTS_2ND_CHANCE FLOAT, "
        "OPP_PTS_FB FLOAT, "
        "OPP_PTS_PAINT FLOAT, "
        "BLKA FLOAT, "
        "PFD FLOAT, "
        #SCORING
        "PCT_FGA_2PT FLOAT, " 
        "PCT_FGA_3PT FLOAT, " 
        "PCT_PTS_2PT FLOAT, " 
        "PCT_PTS_2PT_MR FLOAT, " 
        "PCT_PTS_3PT FLOAT, " 
        "PCT_PTS_FB FLOAT, " 
        "PCT_PTS_FT FLOAT, " 
        "PCT_PTS_OFF_TOV FLOAT, " 
        "PCT_PTS_PAINT FLOAT, " 
        "PCT_AST_2PM FLOAT, " 
        "PCT_UAST_2PM FLOAT, " 
        "PCT_AST_3PM FLOAT, " 
        "PCT_UAST_3PM FLOAT, " 
        "PCT_AST_FGM FLOAT, " 
        "PCT_UAST_FGM FLOAT, " 
        #USAGE
        "USG_PCT_USG FLOAT, "
        "PCT_FGM FLOAT, " 
        "PCT_FGA FLOAT, " 
        "PCT_FG3M FLOAT, " 
        "PCT_FG3A FLOAT, " 
        "PCT_FTM FLOAT, " 
        "PCT_FTA FLOAT, " 
        "PCT_OREB FLOAT, " 
        "PCT_DREB FLOAT, " 
        "PCT_REB FLOAT, " 
        "PCT_AST FLOAT, " 
        "PCT_TOV FLOAT, " 
        "PCT_STL FLOAT, " 
        "PCT_BLK FLOAT, " 
        "PCT_BLKA FLOAT, " 
        "PCT_PF FLOAT, " 
        "PCT_PFD FLOAT, " 
        "PCT_PTS FLOAT, " 
        #FOUR FACTORS
        "EFG_PCT_FF FLOAT, " 
        "FTA_RATE FLOAT, " 
        "TM_TOV_PCT FLOAT, " 
        "OREB_PCT_FF FLOAT, " 
        "OPP_EFG_PCT FLOAT, " 
        "OPP_FTA_RATE FLOAT, " 
        "OPP_TOV_PCT FLOAT, " 
        "OPP_OREB_PCT FLOAT, " 
        #TRACKING
        "SPD FLOAT, " 
        "DIST FLOAT, " 
        "ORBC FLOAT, " 
        "DRBC FLOAT, " 
        "RBC FLOAT, " 
        "TCHS FLOAT, " 
        "SAST FLOAT, " 
        "FTAST FLOAT, " 
        "PASS FLOAT, " 
        "CFGM FLOAT, " 
        "CFGA FLOAT, " 
        "CFG_PCT FLOAT, " 
        "UFGM FLOAT, " 
        "UFGA FLOAT, " 
        "UFG_PCT FLOAT, " 
        "DFGM FLOAT, " 
        "DFGA FLOAT, " 
        "DFG_PCT FLOAT, " 
        #HUSTLE
        "CONTESTED_SHOTS FLOAT, " 
        "CONTESTED_SHOTS_2PT FLOAT, " 
        "CONTESTED_SHOTS_3PT FLOAT, " 
        "DEFLECTIONS FLOAT, " 
        "CHARGES_DRAWN FLOAT, " 
        "SCREEN_ASSISTS FLOAT, " 
        "SCREEN_AST_PTS FLOAT, " 
        "OFF_LOOSE_BALLS_RECOVERED FLOAT, " 
        "DEF_LOOSE_BALLS_RECOVERED FLOAT, " 
        "LOOSE_BALLS_RECOVERED FLOAT, " 
        "OFF_BOXOUTS FLOAT, " 
        "DEF_BOXOUTS FLOAT, " 
        "BOX_OUT_PLAYER_TEAM_REBS FLOAT, " 
        "BOX_OUT_PLAYER_REBS FLOAT, " 
        "BOX_OUTS FLOAT, " 


        "FOREIGN KEY(game_id) REFERENCES Games(game_id),"
        "FOREIGN KEY(player_id) REFERENCES Players(player_id),"
        "PRIMARY KEY(game_id, player_id))")
        
        self.conn.commit()
        



    def create_db_tables(self):
        self.create_Games_Table()
        self.create_Teams_Table()
        self.create_Players_Table()    
        self.create_Lineups_Table()     
        self.create_BoxscoresPlayer_Table()


    def get_num_games(self):
        num_games=0
        c = self.conn.cursor()
        result= c.execute("SELECT count(*) as count1 from GAMES")

        for row in result:
            num_games=row[0]

        return num_games


 



    def check_for_Player_avg_tats_calculation(self):
        c = self.conn.cursor()
        pl_rws = c.execute('SELECT * FROM Players').fetchall() 
        sz_p=len(pl_rws)
        #Check if additional stat columns exist
        if len(pl_rws)>0:
            if len(pl_rws[0])>6:
                #Also check if last row has non zero values
                r_sum = 0
                for i in range(6,len(pl_rws[0])):
                    r_sum=r_sum + (pl_rws[sz_p-1][i] or 0)      
                if r_sum>0:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False



def open_database(dbfile):
    dbms = MyDatabase(dbfile)
    return dbms


def create_season_Database(dbfile):

    #Delete any existing databases first
    if os.path.isfile(dbfile):
        os.remove(dbfile)   


    dbms = MyDatabase(dbfile)

    # Create Tables
    dbms.create_db_tables()
    num_games=dbms.get_num_games() #we return this so we can append the games instead of re-writting

    pl_avg_stats_flag= dbms.check_for_Player_avg_tats_calculation() #check if the season average stats have already been calculated for the teams

    return dbms, num_games, pl_avg_stats_flag



