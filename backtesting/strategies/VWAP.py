"""
    Conditions -----------------
    1. if current close price is above VWAP
    2. if the price before the current price is above VWAP
    3. if the current price is above the sma5
    4. then buy
    5. else, if all the conditions are opposite then sell
"""


from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import talib as talib
import pandas_ta as ta

# TODO: create a funtion to find the slope of the closing price
def slope_of_price(values, n):
    pass


class VWAP(Strategy):
    atr_product = 1.2
    atr_length = 20
    sma_length = 20

    def init(self):
        close = self.data.Close.s
        high = self.data.High.s
        low = self.data.Low.s
        volume = self.data.Volume.s

        self.vwap = self.I(ta.vwap, high=high, low=low, close = close, volume=volume, name='VWAP')
        self.atr = self.I(ta.atr, high=high, low=low, close=close, length=self.atr_length, name='ATR')
        self.sma = self.I(ta.sma, close, length=self.sma_length, name=f'SMA{self.sma_length}')

    def next(self):
        sl_atr = self.atr[-1] * self.atr_product
        TPSLRatio = 1.5

        if not self.position:
            if (self.data.Close[-1] > self.vwap[-1] and
                    self.data.Close[-2] > self.vwap[-2] and
                    self.data.Close[-1] > self.sma[-1]):

                sl = self.data.Close[-1] - sl_atr
                tp = self.data.Close[-1] + TPSLRatio * sl_atr
                self.buy(sl=sl, tp=tp)

            elif (self.data.Close[-1] < self.vwap[-1] and
                  self.data.Close[-2] < self.vwap[-2] and
                  self.data.Close[-1] < self.sma[-1]):

                sl = self.data.Close[-1] + sl_atr
                tp = self.data.Close[-1] - TPSLRatio * sl_atr
                self.sell(sl=sl, tp=tp)


        # # if time is greater than 3:25pm then close all positions
        # if self.data.index[-1].time() > pd.Timestamp('15:25:00').time():
        #     self.position.close()
        #     return
