""" VWAP Scalping strategy

    Conditions -----------------
    1. 5 min timeframe
    2. 15 candles of price should be above or below the VWAP, this is for trend confirmation
    3. bollinder band length 14 standard deviation 2
    4. RSI as confirming signal, RSI < 45 buy, RSI > 55 sell
    5. SL = a * ATR
    6. TP = ratio * SL, ratio = 1.5

    Parameters -----------------
    1. sl, tp
    2. bollinger band lenght, standard deviation
    3. vwap candle no
    4. rsi length
    5. rsi upper limit and lower limit value to close current trade
    6. rsi value to calculate total signal

"""


from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta
import numpy as np

# NOTE: all indicators should return an n array of indicator values

def bollinger_bands(data: pd.Series, length: int = 14, std: int = 2):
    bbands = ta.bbands(close=data, length=length, std=std)
    return bbands.to_numpy().T[0:3]


def vwap_signals(dataframe: pd.DataFrame, vwap_series: np.ndarray, candle_no: int = 15):
    # candle_no is the number of candles to check
    # data is the dataframe
    VWAPsignal = [0]*len(dataframe)
    for row in range(candle_no, len(dataframe)):
        uptrend = 1
        downtrend = 1
        for i in range(row-candle_no, row+1):
            if max(dataframe.Open[i], dataframe.Close[i]) >= vwap_series[i]:
                downtrend = 0
            if min(dataframe.Open[i], dataframe.Close[i]) <= vwap_series[i]:
                uptrend = 0
        if uptrend == 1 and downtrend == 1:
            # sideways trend 3
            VWAPsignal[row] = 0
        elif uptrend == 1:
            # uptrend 2
            VWAPsignal[row] = 1
        elif downtrend == 1:
            # downtrend 1
            VWAPsignal[row] = -1

    return np.asarray(VWAPsignal)


def total_signal(dataframe: pd.DataFrame, vwap_signal: np.ndarray, bbands: np.ndarray, rsi: np.ndarray, candle_no: int = 15):
    TotSignal = [0]*len(dataframe)
    # NOTE: careful backcandles used in vwap_signal function should be same as candle_no here
    for row in range(candle_no, len(dataframe)): 
        if (vwap_signal[row]==1
            and dataframe.Close[row]<=bbands[0][row]
            and rsi[row]<45):
            # if vwap_signal is uptrend & price closes below lower bollinger band & rsi < 45
                TotSignal[row] = 1
        if (vwap_signal[row]==-1
            and dataframe.Close[row]>=bbands[2][row]
            and rsi[row]>55):
            # if vwap_signal is downtrend & price closes above upper bollinger band & rsi > 55
                TotSignal[row] = -1
    return np.asarray(TotSignal)


class VWAP_BB_RSI(Strategy):
    bband_length = 14
    bband_std = 2
    rsi_length = 16
    vwap_signal_length = 15
    atr_length = 7

    def init(self):
        close = self.data.Close.s
        high = self.data.High.s
        low = self.data.Low.s
        volume = self.data.Volume.s

        self.bbands = self.I(bollinger_bands,
                             close, length=self.bband_length, std=self.bband_std,
                             name='Bollinger Bands')

        self.vwap = self.I(ta.vwap,
                           high=high, low=low, close=close, volume=volume,
                           name='VWAP')

        self.rsi = self.I(ta.rsi,
                          close=close, length=self.rsi_length,
                          name='RSI')

        self.vwap_signal = self.I(vwap_signals,
                                  dataframe=self.data.df, vwap_series=self.vwap, candle_no=self.vwap_signal_length,
                                  name='VWAP Signal')
        
        self.total_signal = self.I(total_signal, 
                                    dataframe=self.data.df, vwap_signal=self.vwap_signal, bbands=self.bbands, rsi=self.rsi,
                                    name='Total Signal')
        
        self.atr = self.I(ta.atr, 
                            high=high, low=low, close=close, length=self.atr_length, 
                            name='ATR')

        # type of self.data:  <class 'backtesting._util._Data'>
        # type of self.data.Close:  <class 'backtesting._util._Array'>
        # type of self.data.Close.s:  <class 'pandas.core.series.Series'>

    def next(self):
        sl_atr = self.atr[-1] * 1.2
        TPSLRatio = 1.5

        # looking for exit signals, if we have a position
        if self.position:
            if self.position.is_long and self.rsi[-1] >= 90:
                self.position.close()
            elif self.position.is_short and self.rsi[-1] <= 10:
                self.position.close()

        if not self.position:     
            if self.total_signal[-1] == 1:
                sl = self.data.Close[-1] - sl_atr
                tp = self.data.Close[-1] + TPSLRatio * sl_atr
                self.buy(sl=sl, tp=tp)

            elif self.total_signal[-1] == -1:
                sl = self.data.Close[-1] + sl_atr
                tp = self.data.Close[-1] - TPSLRatio * sl_atr
                self.sell(sl=sl, tp=tp)

        # if time is greater than 3:25pm then close all positions
        if self.data.index[-1].time() > pd.Timestamp('15:15:00').time():
            self.position.close()
            return

        # lower_band = self.bbands[0]
        # middle_band = self.bbands[1]
        # upper_band = self.bbands[2]