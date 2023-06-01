from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import talib as talib
import ta


class NewStrategy(Strategy):
    def init(self):
        pass

    def next(self):
        pass
        # # if time is greater than 3:25pm then close all positions
        # if self.data.index[-1].time() > pd.Timestamp('15:25:00').time():
        #     self.position.close()
        #     return