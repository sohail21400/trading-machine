""" VWAP Scalping strategy
    Conditions -----
    1. 5 min timeframe
    2. 15 candles of price should be above or below the VWAP, this is for trend confirmation
    3. bollinder band length 14 standard deviation 2
    4. RSI as confirming signal, RSI < 45 buy, RSI > 55 sell
    5. SL = a * ATR
    6. TP = ratio * SL, ratio = 1.5
"""
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta
import numpy as np
import pandas_ta as ta


def TotalSignal(df: pd.DataFrame, l):
    if (df.VWAPSignal[l] == 1
        and df.Close[l] <= df['BBL_14_2.0'][l]
            and df.RSI[l] < 45):
        return 1
    if (df.VWAPSignal[l] == -1
        and df.Close[l] >= df['BBU_14_2.0'][l]
            and df.RSI[l] > 55):
        return -1
    return 0


def applyIndicators(df: pd.DataFrame):
    df["VWAP"] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
    df['RSI'] = ta.rsi(df.Close, length=16)
    df['ATR'] = ta.atr(df.High, df.Low, df.Close, length=7)
    my_bbands = ta.bbands(df.Close, length=14, std=2.0)
    df = df.join(my_bbands)

    VWAPsignal = [0]*len(df)
    backcandles = 15

    for row in range(backcandles, len(df)):
        upt = 1
        dnt = 1
        for i in range(row-backcandles, row+1):
            if max(df.Open[i], df.Close[i]) >= df.VWAP[i]:
                dnt = 0
            if min(df.Open[i], df.Close[i]) <= df.VWAP[i]:
                upt = 0
        if upt == 1 and dnt == 1:
            VWAPsignal[row] = 0
        elif upt == 1:
            VWAPsignal[row] = 1
        elif dnt == 1:
            VWAPsignal[row] = -1

    df['VWAPSignal'] = VWAPsignal

    TotSignal = [0]*len(df)
    for row in range(backcandles, len(df)):  # careful backcandles used previous cell
        TotSignal[row] = TotalSignal(df, row)
    df['TotalSignal'] = TotSignal
    return df


# def total_signal(df: pd.DataFrame):
#     return df.TotalSignal.to_numpy()


class VWAP_BB_RSI_Precomputed(Strategy):


    def total_signal(self):
        return self.data.TotalSignal
    
    def rsi(self):
        return self.data.RSI

    def init(self):
        close = self.data.Close.s
        high = self.data.High.s
        low = self.data.Low.s
        volume = self.data.Volume.s

        self.signal1 = self.I(self.total_signal, name='TotalSignal')
        self.rsi = self.I(self.rsi, name='RSI')
        # type of self.data:  <class 'backtesting._util._Data'>
        # type of self.data.Close:  <class 'backtesting._util._Array'>
        # type of self.data.Close.s:  <class 'pandas.core.series.Series'>

    def next(self):
        sl_atr = 1.2 * self.data.ATR[-1]
        TPSLRatio = 1.5

        # looking for exit signals, if we have a position
        if self.position:
            if self.position.is_long and self.data.RSI[-1] >= 90:
                self.position.close()
            elif self.position.is_short and self.data.RSI[-1] <= 10:
                self.position.close()

        if self.signal1 == 1 and not self.position:
            sl = self.data.Close[-1] - sl_atr
            tp = self.data.Close[-1] + TPSLRatio * sl_atr
            self.buy(sl=sl, tp=tp)

        elif self.signal1 == -1 and not self.position:
            sl = self.data.Close[-1] + sl_atr
            tp = self.data.Close[-1] - TPSLRatio * sl_atr
            self.sell(sl=sl, tp=tp)

        # # if time is greater than 3:25pm then close all positions
        # if self.data.index[-1].time() > pd.Timestamp('15:25:00').time():
        #     self.position.close()
        #     return
