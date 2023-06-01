from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta
import numpy as np
from scipy.stats import linregress
import pickle
import xgboost as xgb


class PredictionStrategy(Strategy):
    atr_length = 20
    rsi_length = 16
    backrollingN = 6

    def get_slope(array):
        y = np.array(array)
        x = np.arange(len(y))
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        return slope

    def getSlopeOfIndicator(self, array):
        print(
            '\n\n\n'
        )
        series = pd.DataFrame(array)
        return series.rolling(window=self.backrollingN).apply(self.get_slope, raw=True).values

    def init(self):
        close = self.data.Close.s
        high = self.data.High.s
        low = self.data.Low.s
        volume = self.data.Volume.s

        self.vwap = self.I(ta.vwap,
                           high=high, low=low, close=close, volume=volume,
                           name='VWAP')
        self.rsi = self.I(ta.rsi,
                          close=close, length=self.rsi_length,
                          name='RSI')
        self.atr = self.I(ta.atr,
                          high=high, low=low, close=close, length=self.atr_length,
                          name='ATR')
        self.average = self.I(ta.midprice,
                              high=high, low=low, length=1, talib=False,
                              name='Average')
        self.ma40 = self.I(ta.sma,
                           length=40,
                           close=close,
                           name='MA40')

        self.ma80 = self.I(ta.sma,
                           length=80,
                           close=close,
                           name='MA80')
        self.ma160 = self.I(ta.sma,
                            length=160,
                            close=close,
                            name='MA160')

        self.slopeM40 = self.I(self.getSlopeOfIndicator,
                               array=self.ma40, 
                            #    name='slopeMA40'
                               )
        self.slopeM80 = self.I(self.getSlopeOfIndicator,
                               array=self.ma80, name='slopeMA80')
        self.slopeM160 = self.I(self.getSlopeOfIndicator,
                                array=self.ma160, name='slopeMA160')
        self.slopeAverage = self.I(
            self.getSlopeOfIndicator, array=self.average, name='slopeAverage')
        self.slopeRSI = self.I(self.getSlopeOfIndicator,
                               array=self.rsi, name='slopeRSI')

        self.ma80 = self.I(ta.sma,
                           length=80,
                           name='MA80'
                           )
        self.ma160 = self.I(ta.sma,
                            length=160,
                            name='MA160')


    def next(self):
        # Load the XGBoost model from file
        with open('/Users/sohail21400/Desktop/trading_machine/machine_learning/models/xgb_model.pickle', 'rb') as f:
            model = pickle.load(f)

        df = pd.DataFrame()
        df['ATR'] = self.atr[-1]
        df['RSI'] = self.rsi[-1]
        df['Average'] = self.average[-1]
        df['MA40'] = self.ma40[-1]
        df['MA80'] = self.ma80[-1]
        df['MA160'] = self.ma160[-1]
        df['slopeMA40'] = self.slopeM40[-1]
        df['slopeMA80'] = self.slopeM80[-1]
        df['slopeMA160'] = self.slopeM160[-1]
        df['AverageSlope'] = self.slopeAverage[-1]
        df['RSISlope'] = self.slopeRSI[-1]

        

        sl_atr = self.atr[-1] * 1.5
        TPSLRatio = 1.5

        if not self.position:
            signal = model.predict(df)
            if signal == 2:
                sl = self.data.Close[-1] - sl_atr
                tp = self.data.Close[-1] + TPSLRatio * sl_atr
                self.buy(sl=sl, tp=tp)

            elif signal == 1:
                sl = self.data.Close[-1] + sl_atr
                tp = self.data.Close[-1] - TPSLRatio * sl_atr
                # self.position.close()
                self.sell(sl=sl, tp=tp)
