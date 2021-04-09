import numpy 
import math
import os, sys, inspect
  

class structtype():
    pass


def average_Strategy_Stats(stats):
 
    stats_mean = structtype()
    stats_mean.StrategyName=stats[0].NAME 
    runs=len(stats)

    fields=dir(stats[0]) #get all the fields of the struct (even internals, i.e. those with underlines)
 

    for i in range(1, len(fields)):
        if "__" not in fields[i]: #skip over internal fields of the struct
            V=[]
            for j in range(runs):
                exec("V.append(stats["+str(j)+"]."+fields[i]+")")
            mV=numpy.mean(V)
            exec("stats_mean."+fields[i]+"=mV")

    return stats_mean
        

def SharpeRatio(Asset, Cash):
    #one-dimensional Sharpe ratio calculation. Taken from Matlab's implementation
    Denom =  numpy.nanstd(Asset)+0.000001
    Ratio = 1 / Denom
    Ratio = Ratio * (numpy.nanmean(Asset) - Cash)
    return Ratio
 

def maximumDrawDown(data):
    
    MaxDD=0
    mx = 0
    my = 0
    T=len(data)
    MaxData=data[0]
    MaxIndex=0
    for i in range(T):
        MaxData = max(MaxData, data[i])
        if MaxData == data[i]:
            MaxIndex=i
        DD = (MaxData - data[i]) / MaxData
        if DD > MaxDD:
            MaxDD=DD
            mx= MaxIndex
            my= i


    return MaxDD


def LinearRegression_Score(pl_results, drawDown):
    #Custom score criterion based on linear gains (low risk), avoiding large drawdowns and having many profitable trades. Similar to the objective function used in the Forex
    #Note: Calculate the regression line on the pure profit/loss accumulation graph


    # check for data sufficiency 
    N_trades=len(pl_results)
    if N_trades<3:
        return 0
    
    # create a chart array with an accumulation
    chartline=numpy.zeros(N_trades)
    chartline[0] = pl_results[0]
    for i in range(1,N_trades):
        chartline[i]= chartline[i-1]+pl_results[i]


    # now, Calculate the linear regression y=a*x+b       
    x=0
    y=0
    x2=0
    xy=0

    for i in range(N_trades):
        x=x+i
        y=y+chartline[i]
        xy=xy+i*chartline[i]
        x2=x2+i*i

    a_coef=(N_trades*xy-x*y)/(N_trades*x2-x*x) #slope
    b_coef=(y-a_coef*x)/N_trades               #intercept



    # Calculate mean-square deviation error for specified a and b 
    error=0
    for i in range(N_trades):
        error = error + numpy.power(a_coef*i+b_coef-chartline[i],2)
    std_error=numpy.sqrt(error/(N_trades-2))


    if std_error==0:
        return 0


    # calculate the ratio of trend profits to the standard deviation 
    prof_trades= sum((pl_results>0).astype(int))
    DD=1-drawDown
    return(a_coef*prof_trades*DD/std_error)





def calculate_Strategy_Stats(running_balance,running_stake,min_bet,name,running_bet_with_market,no_games, savings_balance, loading_pcnt):
    stats = structtype()


    stats.NAME=name
    
    #IMPORTANT: make sure the fields of the struct, exept the Name, always start with lowercase

    stats.max_balance=numpy.max(running_balance)
    stats.min_balance=numpy.min(running_balance)
    stats.final_balance=running_balance[-1]

    
    if running_stake: #check if not empty

        stats.maxDD=maximumDrawDown(running_balance)


        stats.growth= (running_balance[-1]-running_balance[0])/running_balance[0]

        stats.mean_balance=numpy.mean(running_balance)
        


        if stats.maxDD==0:
            stats.risk_return_ratio=0
        else:
            stats.risk_return_ratio=stats.growth/stats.maxDD


        balance_diff=numpy.diff(running_balance)
        stats.won=numpy.mean(balance_diff>0) #estimate prediction accuracy by how often balance has increased
        stats.lost=numpy.mean(balance_diff<0) #estimate prediction inaccuracy by how often balance has decreased


        if len(balance_diff[balance_diff<0])==0:
            stats.max_loss=0
            stats.mean_loss=0
        else:
            stats.max_loss=numpy.min(balance_diff[balance_diff<0])
            if (not stats.max_loss) or  numpy.isnan(stats.max_loss):
                stats.max_loss=0
            stats.mean_loss=numpy.mean(balance_diff[balance_diff<0])
            if (not stats.mean_loss) or numpy.isnan(stats.mean_loss):
                stats.mean_loss=0


        if len(balance_diff[balance_diff>0])==0:
            stats.max_profit=0
            stats.mean_profit=0
        else:
            stats.max_profit=max(balance_diff[balance_diff>0])
            if (not stats.max_profit) or numpy.isnan(stats.max_profit):
                stats.max_profit=0
            stats.mean_profit=numpy.mean(balance_diff[balance_diff>0])
            if (not stats.mean_profit) or numpy.isnan(stats.mean_profit):
                stats.mean_profit=0

        if len(balance_diff[balance_diff>0])==0 or len(balance_diff[balance_diff<0])==0:
            stats.profit_factor=0
        else:
            stats.profit_factor= abs(sum(balance_diff[balance_diff>0])/sum(balance_diff[balance_diff<0]))
            if (not stats.profit_factor) or  numpy.isnan(stats.profit_factor):
                stats.profit_factor=0


        stats.max_stake=numpy.max(running_stake)
        stats.min_stake=numpy.min(running_stake)
        stats.total_stake=sum(running_stake)
        stats.avg_stake=numpy.mean(running_stake)

        running_stake_as_pcnt_balance=numpy.divide(running_stake,running_balance[:-1])

        stats.stake_as_pcnt_balance_MAX=numpy.max(running_stake_as_pcnt_balance)
        stats.stake_as_pcnt_balance_MEAN=numpy.mean(running_stake_as_pcnt_balance)

        stats.totalBets=len(numpy.asarray(running_stake)[numpy.asarray(running_stake)>0])

        running_growth=(numpy.asarray(running_balance)-running_balance[0])/running_balance[0]

        stats.sharpe_ratio= SharpeRatio(running_growth, 0.226)

        stats.mean_growth=numpy.mean(running_growth)
        stats.std_growth=numpy.std(running_growth)

        Rn=numpy.diff(numpy.log(running_balance))
        Ravg=numpy.mean(Rn)
        stats.volatility = numpy.sqrt(numpy.sum(numpy.power(Rn-Ravg,2))/len(Rn))

        stats.long_pcnt=numpy.mean(numpy.asarray(running_bet_with_market)==1)
        stats.short_pcnt=numpy.mean(numpy.asarray(running_bet_with_market)==0)

        DL=balance_diff[numpy.asarray(running_bet_with_market)==1]
        DS=balance_diff[numpy.asarray(running_bet_with_market)==0]

        stats.long_Profit=sum(DL[DL>0])
        stats.long_Loss=sum(DL[DL<0])
        stats.short_Profit=sum(DS[DS>0])
        stats.short_Loss=sum(DS[DS<0])

        Stake_Growth=numpy.zeros(len(running_balance)-1)
        for i in range(len(running_balance)-1):
            Stake_Growth[i]=(running_balance[i+1]-running_balance[i])/running_balance[i]
        stats.expected_growth_per_bet=numpy.mean(Stake_Growth)

        if running_balance[-1]<=min_bet:
            stats.ruin=1
        else:
            stats.ruin=0
    

        trade_expecation= stats.won*stats.mean_profit + stats.lost*stats.mean_loss 
        trade_variance=   math.sqrt(stats.won*(stats.mean_profit-trade_expecation)**2 + stats.lost*(stats.mean_loss-trade_expecation)**2)
        if trade_variance==0:
            stats.ev_ratio=0
        else:
            stats.ev_ratio=trade_expecation/trade_variance
 

        stats.savings_balance=  savings_balance

        stats.loading_pcnt_avg =  numpy.mean(loading_pcnt)
        stats.loading_pcnt_max =  numpy.max(loading_pcnt)

        

        #Calculate custom cost function
        stats.lr_score=LinearRegression_Score(balance_diff, stats.maxDD)
        


    else:
        

        stats.maxDD=0
        stats.growth=0
        stats.mean_balance=running_balance[0]
        stats.risk_return_ratio=0
        stats.won=0
        stats.lost=0
        stats.max_loss=0
        stats.mean_profit=0
        stats.max_profit=0
        stats.mean_profit=0
        stats.profit_factor=0 
        stats.max_stake=0
        stats.min_stake=0
        stats.total_stake=0
        stats.avg_stake=0
        stats.stake_as_pcnt_balance_MAX=0
        stats.stake_as_pcnt_balance_MEAN=0  
        stats.totalBets=0
        stats.sharpe_ratio=0 
        stats.mean_growth=0
        stats.std_growth=0
        stats.volatility = 0
        stats.long_pcnt=0
        stats.short_pcnt=0
        stats.long_Profit=0
        stats.long_Loss=0
        stats.short_Profit=0
        stats.short_Loss=0
        stats.mean_loss=0
        stats.expected_growth_per_bet=0
        stats.ruin=0
        stats.ev_ratio=0
        stats.savings_balance=0
    
        stats.lr_score=0
        
        stats.loading_pcnt_avg =  0
        stats.loading_pcnt_max =  0


    return stats
