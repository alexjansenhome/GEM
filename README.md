# GEM

Python implementation of Gary Antonacci's GEM dual momentum strategy as described here: https://www.amazon.com/Gary-Antonacci/e/B00J16UT3W and here: www.optimalmomentum.com

A monthly momentum indicator is given using gem.py, with a variety of lookbacks using ETF data from yahoo (VEU,IVV,BIL,AGG) and also index data from MSCI as comparison/validation since Yahoo Finance has been troublesome lately changing their API and often not giving proper adjusted close data.

The strategy first uses absolute returns to compare 12 month S&P500 returns against cash (1-3 month treasury bill) returns. If cash performed better the strategy invests in intermediate term bonds (Barclay's AGG). If the S&P500 performed beter the strategy employs relative momentum to decide the better of S&P500 and International stocks. 

