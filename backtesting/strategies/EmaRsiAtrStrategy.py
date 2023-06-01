from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import talib as talib
import ta


class EmaRsiAtrStrategy(Strategy):
    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        self.stoch_k = self.I(ta.momentum.stochrsi_k, pd.Series(close))
        self.stoch_d = self.I(ta.momentum.stochrsi_d, pd.Series(close))
        self.EMA_8 = self.I(ta.trend.ema_indicator, pd.Series(close), window=8)
        self.EMA_14 = self.I(ta.trend.ema_indicator,
                             pd.Series(close), window=14)
        self.EMA_50 = self.I(ta.trend.ema_indicator,
                             pd.Series(close), window=50)

        self.ATR = self.I(ta.volatility.average_true_range, pd.Series(
            high), pd.Series(low), pd.Series(close), window=14)
        self.atr = self.I(talib.ATR, high, low, close, timeperiod=14)

    def next(self):
        price = self.data.Close
        try:
            if (crossover(self.stoch_k, self.stoch_d) and
                price > self.EMA_8 and crossover(self.EMA_8, self.EMA_14) and
                    crossover(self.EMA_14, self.EMA_50)):
                sl = price - self.ATR * 3
                tp = price + self.ATR * 2
                self.buy(sl=sl, tp=tp)

            elif (crossover(self.stoch_d, self.stoch_k) and
                  price < self.EMA_8 and
                  crossover(self.EMA_14, self.EMA_8) and
                    crossover(self.EMA_50, self.EMA_14)):

                sl = price + self.ATR * 3
                tp = price - self.ATR * 2
                self.sell(sl=sl, tp=tp)

        except Exception as e:
            print(e)
