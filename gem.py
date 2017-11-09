import json
import pandas
import requests
import re

fetch=True

def filter_end_of_month(df):
    # get end of month and most recent value only since early 2016
    df=df[df.index>='2016-03-01']
    newindex = []
    for i in range(0, len(df.index) - 1):
        if df.index[i].month != df.index[i + 1].month:
            newindex.append(df.index[i])
    if df.index[len(df.index) - 1].month != newindex[len(newindex) - 1].month:
        newindex.append(df.index[len(df.index) - 1])
    return df[df.index.isin(newindex)]

# AGG Adjusted close
# curl "http://mschart.morningstar.com/chartweb/defaultChart?type=getcc&secids=XIUSA000MC;XI&dataid=117&startdate=1900-01-01&enddate=2099-01-01&format=1&adjustment=-1"
if fetch:  # only when to refresh data for a new day, to avoid keeping going to server
    r = requests.get('http://mschart.morningstar.com/chartweb/defaultChart?type=getcc&secids=XIUSA000MC;XI&dataid=117&startdate=1900-01-01&enddate=2099-01-01&format=1&adjustment=-1')
    with open('agg.json','w') as data_file:
        data_file.write(r.text)
with open('agg.json') as data_file:
    agg = json.load(data_file)

agg_index=[]
agg_vals=[]
for r in agg["data"]["r"]:
    for t in r["t"]:
        for d in t["d"]:
            agg_index.append(d['i'])
            agg_vals.append(d['v'])

agg = pandas.DataFrame(index=pandas.DatetimeIndex(agg_index),data=agg_vals,columns = ['Adj Close'],dtype=float)
agg=agg['Adj Close']

# MSCI US and World-ex-US, Gross, Adjusted Close
# curl "https://www.msci.com/webapp/indexperf/charts?indices=2669%2CC%2C36%7C104%2CC%2C30&baseValue=false&format=CSV&currency=15&priceLevel=40&endDate=23%20Jun%2C%202017&frequency=D&startDate=03%20MAR%2C%202016&site=gimi&scope=R"
if fetch:
    r=requests.get('https://www.msci.com/webapp/indexperf/charts?indices=2669%2CC%2C36%7C104%2CC%2C30&baseValue=false&format=CSV&currency=15&priceLevel=40&endDate=23%20Jun%2C%202099&frequency=D&startDate=03%20JAN%2C%202016&site=gimi&scope=R')
    with open('msci.csv','w') as data_file:
        data_file.write(r.text)

msci = pandas.read_csv('msci.csv', header=None, thousands=',')
msci=msci.T.iloc[::2][1::].set_index(pandas.DatetimeIndex(msci.T.iloc[1::2][0].values))

# 1 year treasury yield DGS1 (Date, yield), always excludes last month
if fetch:
    r=requests.get('https://fred.stlouisfed.org/graph/fredgraph.csv?cosd=1970-01-01&mode=fred&id=DGS1')
    with open('DGS1.csv','w') as data_file:
        data_file.write(r.text)

treas=pandas.read_csv('DGS1.csv', parse_dates=True, index_col=0, na_values='.') # . is a NaN
treas=treas[treas['DGS1']==treas['DGS1']] # filter out the NaN's

# GOLD (loaded here but not used here but in adaptive_allocation.py)
if fetch:
    r=requests.get('https://fred.stlouisfed.org/graph/fredgraph.csv?cosd=1970-01-01&mode=fred&id=GOLDPMGBD228NLBM')
    with open('GOLD.csv','w') as data_file:
        data_file.write(r.text)
gold=pandas.read_csv('GOLD.csv', parse_dates=True, index_col=0, na_values='.') # . is a NaN
gold=gold[gold['GOLDPMGBD228NLBM']==gold['GOLDPMGBD228NLBM']] # filter out the NaN's

lastdate=msci.index[-1]

# adjust AGG and TREAS last date if less than MSCI, MSCI is most important in judging, and most volatile
if agg.index[-1] < lastdate:
    # create a 1-row dataframe and append it
    to_append=agg[-1:]
    ndx = to_append.index.values.copy()
    ndx[-1] = lastdate
    to_append.index = ndx
    agg=agg.append(to_append)

if treas.index[-1]<lastdate:
    # create a 1-row dataframe and append it
    to_append=treas[-1:]
    ndx = to_append.index.values.copy()
    ndx[-1] = lastdate
    to_append.index = ndx
    treas=treas.append(to_append)

#assume we can exchange every month, approximation but should be sufficient
treas=filter_end_of_month(treas)
pv=100.0
for i in range(0,len(treas.index)):
    interest=treas.iloc[i]['DGS1']
    nv=pv*(1.+interest/(12.*100.))
    treas.ix[i,'DGS1']=nv
    pv=nv

msci.index.name = 'Date'
msci=msci[msci.index.isin(treas.index)]
agg=agg[agg.index.isin(treas.index)]

msci=msci.join(agg).join(treas)
msci.columns=['MSCI_ACW_XUS','MSCI_US','AGG_BONDS','1YR_TREAS']
msci=msci[['1YR_TREAS','MSCI_US','MSCI_ACW_XUS','AGG_BONDS']]

msci.to_csv('monthly_adjusted_close.csv')

#curl -v "https://finance.yahoo.com/quote/ACWX/history?p=ACWX" > x.txt
#Returns cookie in header and CrumbStore (search for) crumb in x.txt
#curl 'https://query1.finance.yahoo.com/v7/finance/download/ACWX?period1=1400463852&period2=2495055852&interval=1d&events=history&crumb=VUaMGEPt54h' -H 'cookie: B=2lejvulcl3a76&b=3&s=sp'

funds=['BIL','IVV','VEU','AGG' ]
#funds=['VOO','VGK','VPL','VWO','RWO', 'DBC','IAU', 'VGIT','VGLT','VWOB','IGOV', 'SCHP', 'WIP','BND','BNDX' ]
#funds=['PEBIX', 'PFOAX', 'PRRIX', 'VGSIX', 'VEURX', 'VPACX', 'VFINX','VEIEX', 'VUSTX', 'VBMFX' ]

if fetch:
    # old sample
    #cookie='B=eueknj1cqlmaq&b=3&s=1n'
    #crumb='qdi2OcVtqhU'

    crumb=''
    p=re.compile('\w{11}') # seems we need an all alpha-numeric crumb of length 11, so without \u0010 etc
    while not p.match(crumb):
        cookie_request = requests.get("https://finance.yahoo.com/quote/ACWX/history?p=ACWX")
        cookie = cookie_request.headers['set-cookie'].split()[0][:-1]
        crumb_string = '"CrumbStore":{"crumb":"'
        crumb_start = cookie_request.text.find(crumb_string) + len(crumb_string)
        crumb_end = cookie_request.text.find('"', crumb_start)
        crumb = cookie_request.text[crumb_start:crumb_end]
        # print cookie, crumb

    headers={'cookie': cookie}
    for f in funds:
        r = requests.get('https://query1.finance.yahoo.com/v7/finance/download/'+f+\
                            '?period1=315637200&period2=3178497600&interval=1d&'+\
                            'events=history&crumb='+crumb,
                          headers=headers)
        with open(f+'.csv', 'w') as data_file:
            data_file.write(r.text)

data={}
for f in funds:
    df = pandas.read_csv(f+'.csv', thousands=',', index_col=0, na_values='null')
    df = df[df['Adj Close'] == df['Adj Close']]
    df.index=pandas.DatetimeIndex(df.index)
    df=filter_end_of_month(df)[['Adj Close']]
    df.columns=[f]
    data[f]=df

yahoo=data['BIL'].join(data['IVV']).join(data['VEU']).join(data['AGG'])
try:
    yahoo.to_csv('yahoo_monthly_adjusted_close.csv')
except:
    print(">>>Error: could not write yahoo_monthly_adjusted_close.csv")

print (msci)
print (yahoo)

msci12=100*(msci.iloc[-1]-msci.iloc[-13])/msci.iloc[-13]
yahoo12=100*(yahoo.iloc[-1]-yahoo.iloc[-13])/yahoo.iloc[-13]
print
print ("12 month returns (%):")
print (msci12.to_frame().T)
print (yahoo12.to_frame().T)

msci6=100*(msci.iloc[-1]-msci.iloc[-7])/msci.iloc[-7]
yahoo6=100*(yahoo.iloc[-1]-yahoo.iloc[-7])/yahoo.iloc[-7]
print
print ("6 month returns (%):")
print (msci6.to_frame().T)
print (yahoo6.to_frame().T)

df = pandas.DataFrame(columns=msci.columns)
for i in range(13):
    df.loc[i+1] = [ 100*(msci[n].iloc[-1]-msci[n].iloc[-i-2])/msci[n].iloc[-i-2] for n in msci.columns]
print(df)


df = pandas.DataFrame(columns=yahoo.columns)
for i in range(13):
    df.loc[i+1] = [ 100*(yahoo[n].iloc[-1]-yahoo[n].iloc[-i-2])/yahoo[n].iloc[-i-2] for n in yahoo.columns]
print(df)

