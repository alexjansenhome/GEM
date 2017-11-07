import datetime
import pandas
import math
import matplotlib.pyplot as plt
from matplotlib import interactive

# load datasets
monthlies1970 = pandas.read_csv('msci_all_gross.csv', thousands=",", decimal=".", index_col=0, skiprows=2,
                                parse_dates=True)
monthlies1926 = pandas.read_csv('monthly_1926.csv', thousands=",", decimal=".", index_col=0, skiprows=2,
                                parse_dates=True)

# analyze an investment resultset "result", dates provides in "monthlies"
def analyze_run(result, monthlies, bDetails):
    if (bDetails): print ("--------------------------------------------------------------------------------------------------------")
    if (bDetails): print ("Min and Max returns by duration")
    if (bDetails): print ("--------------------------------------------------------------------------------------------------------")
    bounds = []
    for dur in range(1, 482):
        gain_min = +100000000000.
        gain_max = -100000000000.
        gain_avg = 0.
        dmin = 0
        for win in range(0, len(result) - dur - 1):
            gain = (result[win + dur] - result[win]) / result[win]
            if gain < gain_min:
                dmin = win
                gain_min = gain
            if gain > gain_max:
                gain_max = gain
            gain_avg=gain_avg+gain
        gain_avg=gain_avg/(len(result)-dur-1)
        bounds.append({'min': gain_min, 'mindate': dmin, 'avg':gain_avg, 'max':gain_max})
        if dur % 12 == 0 and bDetails:
            print ("%3d months (%4.1f years; date: %s): %7.1f%%-%7.1f%% (%6.2f%%-%6.2f%% annual return; %6.2f%% avg)" % \
                  (dur, dur / 12., str(monthlies[dmin])[0:10], gain_min * 100., gain_max * 100.,
                   (math.pow(1. + gain_min, 12. / dur) - 1) * 100.,
                   (math.pow(1. + gain_max, 12. / dur) - 1) * 100.,
                   (math.pow(1. + gain_avg, 12. / dur) - 1) * 100.))

    if (bDetails): print ("--------------------------------------------------------------------------------------------------------")
    if (bDetails): print ("Worst case returns by duration")
    if (bDetails): print ("--------------------------------------------------------------------------------------------------------")

    worstTotal = []
    worstAnnualized = []
    worstStart = []
    avgAnnualized=[]
    for dur in range(1, 481):
        gain_min = math.pow(1. + bounds[dur]['min'], 12. / dur) - 1
        gain_avg = math.pow(1. + bounds[dur]['avg'], 12. / dur) - 1
        dur_min = bounds[dur]['mindate']
        for dur2 in range(dur, 481):
            if math.pow(1. + bounds[dur2]['min'], 12. / dur2) - 1 < gain_min:
                dur_min = bounds[dur2]['mindate']
                gain_min = math.pow(1. + bounds[dur2]['min'], 12. / dur2) - 1
        if dur % 12 == 0 and bDetails:
            print ("%3d months (%4.1f years; date: %s): %6.1f%% (%6.2f%% annual return; %6.2f%% avg annual return)" % \
                  (dur, dur / 12., str(monthlies[dur_min])[0:10],
                   (math.pow(1 + gain_min, dur / 12.) - 1) * 100., gain_min * 100., gain_avg*100.) )
        if dur % 120 == 0:
            worstTotal.append((math.pow(1 + gain_min, dur / 12.) - 1) * 100.)
            worstAnnualized.append(gain_min * 100.)
            worstStart.append(str(monthlies[dur_min])[0:10])
            avgAnnualized.append(gain_avg * 100.)

    maxdown_pct = 0  # max drawdown in %
    maxdown_pct_end = 0  # when max drawdown by % ends
    maxdown_pct_start = 0  # start of max drawdown in %
    curdown_pct_start = 0  # start of current drawdown by % stretch

    maxdown_len = 0  # longest drawdown stretch
    maxdown_len_start = 0  # start of longest drawdown stretch
    curdown_len_start = 0  # start of current drawdown by duration stretch

    for d in range(0, len(result) - 1):

        # first find longest downstretch
        if result[d] < result[curdown_len_start]:  # still in down-stretch?
            if maxdown_len < d - curdown_len_start:  # longest down-stretch found so far?
                maxdown_len = d - curdown_len_start
                maxdown_len_start = curdown_len_start
        else:  # no more down-stretch, so reset
            curdown_len_start = d

        # now find maximum drawdown %
        if result[d] < result[curdown_pct_start]:  # still in down-stretch?
            if (result[d] - result[curdown_pct_start]) / result[curdown_pct_start] < maxdown_pct:
                maxdown_pct = (result[d] - result[curdown_pct_start]) / result[curdown_pct_start]
                maxdown_pct_start = curdown_pct_start
                maxdown_pct_end = d
        else:  # no more down-stretch. so reset
            curdown_pct_start = d

    years = (len(result)-1) / 12.
    if bDetails:
        print ("--------------------------------------------------------------------------------------------------------")
        print ("Results:")
        print ("- Return=%5.2f%% for %5.2f years (100K => %dM)" % (
            (math.pow(result[-1] / result[0], 1 / years) - 1) * 100., years, result[-1] / result[0]) )
        print ("- Maximum drawdown duration until full recovery=%.1f years; Start=%s" % (
            maxdown_len / 12., str(monthlies[maxdown_len_start])[0:10]) )
        print ("- Maximum drawdown by amount=%.2f%% for %.1f years (Start=%s, End=%s)" % (
            maxdown_pct * 100., (maxdown_pct_end - maxdown_pct_start + 1) / 12.,
        str(monthlies[maxdown_pct_start])[0:10], str(monthlies[maxdown_pct_end - 1])[0:10]) )

        for i in range(0, len(worstTotal)):
            print ("- Worst %d years: Start=%s Total=%6.1f%% Annual=%5.2f%%" % (
                (i + 1) * 10, worstStart[i], worstTotal[i], worstAnnualized[i]) )
        print ("--------------------------------------------------------------------------------------------------------")

    all_result = [maxdown_len, maxdown_pct, (math.pow(result[-1] / result[0], 1 / years) - 1) * 100.]

    for i in range(0, len(worstTotal)):
        all_result.append(worstStart[i])
        all_result.append(worstTotal[i])
        all_result.append(worstAnnualized[i])
        all_result.append(avgAnnualized[i])
    all_result.append(result)

    return all_result



#----------------------------------------------------------------------------------------------------------------
# one single run
# bDetails: Print detail results
# momentums: momentum ranges (divide money in portions) (-1=all bonds, -2 =all S&P500, -3=all foreign stocks, otherwise # of momentum months)
# b1970: start in 1970 or 1926. 1970 has foreign stocks, 1926 has not
# bInflationAdjusted: inflation adjusted results?
# bMovingAverage use moving average (in # of months) as extra safeguard for momentum based portions?

def run(bDetails, momentums, b1970, bInflationAdjusted, movingAverage, vigilant):
    if b1970:
        monthlies = monthlies1970
        startdate = datetime.datetime(1970, 12, 1)
        lastdate=datetime.datetime(2099,1,1)
        foreign = 3
        sp500 = 7
        bonds = 10
        inflation = 14
        bills = 15
    else:
        monthlies = monthlies1926
        startdate = datetime.datetime(1927, 1, 1) #1927 or higher
        lastdate=datetime.datetime(2099,1,1)
        foreign = 0
        sp500 = 3
        bonds = 6
        bills = 9
        inflation = 12
    # moving averages
    rm = monthlies.rolling(window=movingAverage, center=False).mean()

    current_alloc = []  # fund and # of shares in fund (initially no allocations and just cash)
    prev_cash = 100000.
    result = [prev_cash]  # sequence of monthly ending values, to derive statistics later on

    # only if we calculate inflation-adjusted returns
    prev_inflation = 0.

    if (bDetails): print ("--------------------------------------------------------------------------------------------------------")
    if (bDetails): print ("End-of-month decisions and value")
    if (bDetails): print ("--------------------------------------------------------------------------------------------------------")

    base = 0  # starting index
    months=0
    num_bonds=[0,0] # # of
    for date in monthlies.index:

        if date >= startdate and date<lastdate:
            idx_now = monthlies.index.get_loc(date)
            row_now = monthlies.iloc[idx_now]
            row_rm = rm.iloc[rm.index.get_loc(date)]

            # first calc final valuation at end of this month
            cash = 0.
            for pair in current_alloc:
                if pair[1] != 0:
                    cash = cash + pair[1] * row_now[pair[0]]
            if cash == 0.:
                cash = prev_cash

            # inflation adjusted cash
            current_inflation = row_now[inflation]
            if bInflationAdjusted and prev_inflation > 0:
                cash = (prev_inflation / current_inflation) * cash

            # 1 allocation per momentum duration
            current_alloc = []
            funds = ""

            for m in momentums:
                if m == -1:  # use bonds for this subset
                    current = bonds
                    fund = "Bonds"
                elif m == -2:  # use all stocks for this subset
                    current = sp500
                    fund = "S&P500"
                elif m == -3 and foreign > 0:  # use all foreign for this subset, only for >1970
                    current = foreign
                    fund = "Foreign"
                else:  # use momentum to decide
                    row_prev = monthlies.iloc[idx_now - m]
                    m_foreign = 0

                    """
                    if foreign > 0:
                        m_foreign = (math.pow(1 + (row_now[foreign] - row_prev[foreign]) / row_prev[foreign], 12 / m) - 1)
                    m_sp500 = (math.pow(1 + (row_now[sp500] - row_prev[sp500]) / row_prev[sp500], 12 / m) - 1)
                    m_bonds = (math.pow(1 + (row_now[bonds] - row_prev[bonds]) / row_prev[bonds], 12 / m) - 1)
                    m_bills = (math.pow(1 + (row_now[bills] - row_prev[bills]) / row_prev[bills], 12 / m) - 1)
                    """

                    if foreign > 0:
                        m_foreign = (row_now[foreign] - row_prev[foreign]) / row_prev[foreign]
                    m_sp500 = (row_now[sp500] - row_prev[sp500]) / row_prev[sp500]
                    m_bonds = (row_now[bonds] - row_prev[bonds]) / row_prev[bonds]
                    m_bills = (row_now[bills] - row_prev[bills]) / row_prev[bills]

                    if (m_sp500 >= m_bills) and \
                       (not(vigilant) or m_bonds>=m_bills) and \
                       (movingAverage == 0 or row_rm[sp500] <= row_now[sp500]):
                        if foreign == 0 or m_sp500 >= m_foreign:
                            current = sp500
                            fund = "S&P500"
                        else:
                            current = foreign
                            fund = "Foreign"
                    else:
                        current = bonds
                        fund = "Bonds"

                funds = funds + ("%8s" % fund)
                num_shares = (cash / len(momentums)) / row_now[current]
                current_alloc.append([current, num_shares])

            months+=1
            annualized=100*(math.pow(1 + (cash - 100000.) / 100000., 12 / months) - 1)
            s = str(date)[0:10] + "%10.0f, %6.2f %6.2f  (%s)" % \
                                  (cash, (cash - prev_cash) * 100. / prev_cash, annualized , funds)
            if (bDetails): print (s)

            prev_cash = cash
            result.append(cash)
            prev_inflation = current_inflation
        else:
            base = base + 1

    monthlies=monthlies[base-1:]

    if bDetails:
        print ("Input parameters:")
        print ("- S&P500/Bonds (Absolute momentum) since" if not (
        b1970) else "- S&P500/Foreign Stocks/Bonds (Dual momentum) since"), str(startdate)[0:10]
        print ("- Inflation Adjusted" if bInflationAdjusted else "- Not inflation adjusted")
        print ("- Moving Average Safeguard: %d" % movingAverage)
        tranches = ""
        for m in momentums:
            if m == -1:
                tranches = tranches + "Bonds "
            elif m == -2:
                tranches = tranches + "S&P500 "
            elif m == -3:
                tranches = tranches + "Foreign "
            else:
                tranches = tranches + ("Mom-%02d " % m)
        print ("- Tranches: %s" % tranches)
        print ("--------------------------------------------------------------------------------------------------------")

    return [b1970, bInflationAdjusted, movingAverage, momentums, vigilant] + analyze_run(result, monthlies.index, bDetails)



#----------------------------------------------------------------------------------------------------------------
# set of scenarios, -2=bonds, -1=stocks, >0=momentum window

bDetails=False
# -2=all stocks
# -1=all bonds
# -1,-1,-2,-2,-2 = 60 stocks/40 bonds
# 12=GEM 12 months
# [6,12]= 50% GEM 6 months, 50% GEM 12 months
# 6=GEM 6 months
# -1,6,12= 33% bonds, 33% GEM 6 months, 33% GEM 12 months


momentum_set=[[-2], [-1], [-1, -1, -2, -2, -2], [12], [6,12], [6], [-1,6,12] ]
movingAverage_set=[0]

all_results=[]
for momentums in momentum_set:
    for b1970 in [True,False]:
        for bInflationAdjusted in [False,True]:
            for bVigilant in [False,True]:
                for movingAverage in movingAverage_set:
                    if not(movingAverage) or not(momentums in [[-1],[-2],[-1,-1,-2,-2,-2]]):
                        print ("%3d / %3d" % (len(all_results)+1, 2*2*2*len(movingAverage_set)*len(momentum_set)))
                        all_result=run(False,momentums,b1970,bInflationAdjusted,movingAverage,bVigilant)
                        all_results.append(all_result)


for bInflationAdjusted in [False,True]:
    print ("=========================")
    print ("Inflation Adjusted" if (bInflationAdjusted) else "Not inflation adjusted")
    print ("=========================")
    for b1970 in [True,False]:
        print ("-----------------------------")
        print ("Dual momentum since 1970" if b1970 else "Absolute momentum since 1926")
        print ("-----------------------------")
        print ("%30s    : maxddyr maxdd%% Total%%   Min10%%   Min20%%   Min30%%  |  Avg10%%   Avg20%%   Avg30%%" % ("allocation"))
        print ("---------------------------------------------------------------------------------------------------------------")
        for r in all_results:
                for m in momentum_set:
                    for v in [False]:
                        for movingAverage in movingAverage_set:
                            if r[0] == b1970 and r[1] == bInflationAdjusted and r[2]==movingAverage and r[3]==m and r[4]==v:
                                print ("%30s%1s%2s: %6.1f %5.2f%% %5.2f%%   %5.2f%%   %5.2f%%   %5.2f%%  |  %5.2f%%   %5.2f%%   %5.2f%%" % \
                                    (str(m),('V' if v else ' '),( ('MA%02d'%movingAverage) if movingAverage>0 else '    '),
                                    r[5]/12.,r[6]*100.,r[7], r[10], r[14], r[18], r[11], r[15], r[19]) )

exit()


#----------------------------------------------------------------------------------------------------------------
# one single test run

#def run(bDetails, momentums, b1970, bInflationAdjusted, movingAverage, vigilant):

#run(True,[-2],False,False,0,False)
run(True,[12],False,False,0,False)
exit()

#----------------------------------------------------------------------------------------------------------------
# a few runs, compare in graphs

dur=72
b1970=True
bInflation=False
ma=0
moms=[ [-1], [6,12], [6], [12], [3,6,9,12],  [-1,6,12] ]
for m in moms:
    res=run(False,m,b1970,bInflation,ma,False)
    set=res[len(res)-1]
    rolling_return=[]
    for n in range(0,len(set)-dur-1):
        rolling_return.append(100.*(math.pow(set[n+dur]/set[n],1./(dur/12))-1))
    series=pandas.Series(rolling_return,
        index=(monthlies1970.index[:len(rolling_return)] if b1970 else monthlies1926.index[:len(rolling_return)]))
    if m==[-1]:
        s="Bonds"
    elif m==[-2]:
        s="S&P500"
    elif m==[-3]:
        s="ACWX"
    else:
        s="Mom"+str(m)
    plt.plot(series, label=s)

plt.legend()
plt.show()
interactive(True)

