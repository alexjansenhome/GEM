# GEM

Python implementation of Gary Antonacci's GEM ("Global Equities Momentum") dual momentum strategy as described in his best seller
https://www.amazon.com/Dual-Momentum-Investing-Innovative-Strategy/dp/0071849440 and his blog: www.optimalmomentum.com.

The strategy first uses absolute returns to compare 12 month S&P500 returns against cash (1-3 month treasury bill) returns. If cash performed better the strategy invests in intermediate term bonds (Barclay's AGG). If the S&P500 performed better the strategy employs relative momentum to invest in the better of S&P500 and International stocks. Decisions are made on the last trading day of each month.

gem.py: A monthly momentum indicator, with a variety of lookbacks using ETF data from yahoo (VEU,IVV,BIL,AGG) and index data from MSCI as comparison/validation (Yahoo Finance has been unreliable lately, changing their API and often not giving proper adjusted close data).

gem_backtest.py: Python backtest code using historic data going back to either 1970 for dual momentum or 1926 for absolute momentum (no historic international data available pre-1970). Historic data is available in the 2 .csv files in this project. The code runs through several scenarios, illustrating the almost to-good-to-be-true performance of GEM against more traditional strategies such as 60%/40% stocks/bonds or even 100% stock investments.



