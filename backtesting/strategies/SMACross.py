from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    sma_length1 = 10
    sma_length2 = 20
    atr_length = 14
    
    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.sma_length1, name=f'SMA {self.sma_length1}')
        self.sma2 = self.I(SMA, self.data.Close, self.sma_length2, name=f'SMA {self.sma_length2}')
        self.atr = self.I(ta.atr, 
                            high=self.data.High.s, low=self.data.Low.s, close=self.data.Close.s, length=self.atr_length, 
                            name=f'ATR {self.atr_length}')
    
    def next(self):
        sl_atr = self.atr[-1] * 1.5
        TPSLRatio = 1.5

        if not self.position:
            # If sma1 crosses above sma2, close any existing
            # short trades, and buy the asset
            if crossover(self.sma1, self.sma2):
                sl = self.data.Close[-1] - sl_atr
                tp = self.data.Close[-1] + TPSLRatio * sl_atr
                self.buy(sl=sl, tp=tp)

            # Else, if sma1 crosses below sma2, close any existing
            # long trades, and sell the asset
            elif crossover(self.sma2, self.sma1):
                sl = self.data.Close[-1] + sl_atr
                tp = self.data.Close[-1] - TPSLRatio * sl_atr
                self.position.close()
                self.sell(sl=sl, tp=tp)

    # CLASSICAL WAY OF DEFINING STRATEGY
    # def next(self):
    #     if (self.sma1[-2] < self.sma2[-2] and
    #             self.sma1[-1] > self.sma2[-1]):
    #         self.position.close()
    #         self.buy()

    #     elif (self.sma1[-2] > self.sma2[-2] and    # Ugh!
    #           self.sma1[-1] < self.sma2[-1]):
    #         self.position.close()
    #         self.sell()