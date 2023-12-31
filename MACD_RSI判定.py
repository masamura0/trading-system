import pandas_datareader.data as pdr
import plotly.graph_objs as go
import talib as ta
import datetime as dt
import pandas as pd
import numpy as np
import tkinter as tk
from datetime import datetime

##############################################################
def get_stock_data(code):
  df = pdr.DataReader("{}.JP".format(code), "stooq").sort_index()
  return df

##############################################################
def on_click_execute():
  entered_code = int(entry_code.get())
  entered_date = entry_date.get()
  entered_date = datetime.strptime(entered_date, "%Y,%m,%d")

  df = get_stock_data(entered_code)
  close = df["Close"]

  # 5日間の変動率を計算
  df['5日間の変動率'] = df['Close'].pct_change(periods=5)
  df['リスク'] = pd.cut(df['5日間の変動率'], bins=[-np.inf, 0.3, 0.4, np.inf], labels=['低リスク', '中リスク', '高リスク'])

##############################################################
# 5日、25日、50日、75日、200日移動平均の算出
  ma5 = ta.SMA(close, timeperiod=5)
  df["ma5"] = ma5
  ma25 = ta.SMA(close, timeperiod=25)
  df["ma25"] = ma25
  ma50 = ta.SMA(close, timeperiod=50)
  df["ma50"] = ma50
  ma75 = ta.SMA(close, timeperiod=75)
  df["ma75"] = ma75
  ma200 = ta.SMA(close, timeperiod=200)
  df["ma200"] = ma200

# MACD、シグナル、ヒストグラムを算出
  macd, macdsignal, hist = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
  df["macd"] = macd
  df["macd_signal"] = macdsignal
  df["hist"] = hist

# RSI
  rsi14 = ta.RSI(close, timeperiod=14)
  rsi28 = ta.RSI(close, timeperiod=28)
  df["rsi14"], df["rsi28"] = rsi14, rsi28
  df["80"],  df["20"] = [80 for _ in close], [20 for _ in close]

##############################################################
  rdf = df[dt.datetime(2020,1,1):dt.datetime(entered_date.year, entered_date.month, entered_date.day)]
  rdf.index = pd.to_datetime(rdf.index).strftime("%m-%d-%Y")

##############################################################
# ma5がma50を上に交差するポイントを見つける
  crossing_points = np.where((rdf['ma5'].shift(1) < rdf['ma50'].shift(1)) & (rdf['ma5'] > rdf['ma50']))[0]

# グラフのデータを設定する前に、紫のまるいマーカーを追加する
  crossing_dates = rdf.iloc[crossing_points].index

# MACDがシグナルを上に交差したポイント
  macd_above_signal = np.where((rdf['macd'].shift(1) < rdf['macd_signal'].shift(1)) & (rdf['macd'] > rdf['macd_signal']))[0]
# MACDがシグナルを下に交差したポイント
  macd_below_signal = np.where((rdf['macd'].shift(1) > rdf['macd_signal'].shift(1)) & (rdf['macd'] < rdf['macd_signal']))[0]

# 上に交差したポイントを赤丸で表記
  macd_above_dates = rdf.iloc[macd_above_signal].index
# 下に交差したポイントを❌で表記
  macd_below_dates = rdf.iloc[macd_below_signal].index

# MACDの振幅を計算
  macd_amplitude = rdf['macd'] - rdf['macd_signal']

# リスクを判定してラベル付け
  rdf.loc[:, 'リスク'] = pd.cut(macd_amplitude, bins=[-np.inf, -3, -2, -1, 1, 2, 3, np.inf],
  labels=['極めて高いリスク', '高いリスク', 'やや高いリスク', '安定', 'やや低いリスク', '低いリスク', '極めて低いリスク'])

# RSIが35以下のときは「買い」、65以上のときは「売り」、それ以外は「どちらでもない」と判定する
  latest_rsi_decision = np.where(rdf.iloc[-1]['rsi14'] <= 35, '買い', np.where(rdf.iloc[-1]['rsi14'] >= 65, '売り', 'どちらでもない'))

# リスクに基づいて色を設定
  risk_color_map = {
      '極めて高いリスク': 'red',
      '高いリスク': 'orange',
      'やや高いリスク': 'yellow',
      '安定': 'green',
      'やや低いリスク': 'blue',
      '低いリスク': 'indigo',
      '極めて低いリスク': 'violet'
  }  

##############################################################
  layout = {
      "height": 1000,
      "title": {"text": str(entered_code), "x": 0.5},
      "xaxis": {"rangeslider": {"visible": False}},
      "yaxis1": {"domain": [0.46, 1.0], "title": "価格（円）", "side": "left", "tickformat": ","},
      "yaxis2": {"domain": [0.30, 0.395], "title": "MACD", "side": "right"},
      "yaxis3": {"domain": [0.20, 0.295], "title": "RSI", "side": "right"},
      "yaxis4": {"domain": [0.10, 0.195], "title": "Volume", "side": "right"},
      "plot_bgcolor": "lightblue",
  }
  annotations = [
          {
            "xref": 'paper',
            "yref": 'paper',
            "x": 1.0,  # 右端に寄せるための x 座標の調整
            "y": 1.0,  # 上端に寄せるための y 座標の調整
            "text": f"{row['リスク']}",
            "showarrow": False,
            "font": dict(color='black', size=20),
            "align": 'center',
            "bgcolor": risk_color_map.get(row['リスク'], 'lightgray'),
            "bordercolor": 'black',
            "borderwidth": 1,
            "borderpad": 4,
            "xshift": 10
          }
          for _, row in rdf.groupby('リスク').last().reset_index().iterrows()
      ]
# ラベルを表示する処理を追加
  annotations += [
      {
          "xref": 'paper',
          "yref": 'paper',
          "x": 1.0,
          "y": 0.95,  # 右上に表示
          "text": f"RSI判定: {latest_rsi_decision}",
          "showarrow": False,
          "font": dict(color='black', size=20),
          "align": 'right',
          "bgcolor": 'lightgray',
          "bordercolor": 'black',
          "borderwidth": 1,
          "borderpad": 4,
          "xshift": -10  # ラベルを右に寄せる
      }
  ]

  layout['annotations'] = annotations
  
  ##############################################################
  data =  [
              # ローソク足
              go.Candlestick(yaxis="y1", x=rdf.index, open=rdf["Open"], high=rdf["High"], low=rdf["Low"], close=rdf["Close"],
                              increasing_line_color="red", decreasing_line_color="gray"),

              # 5日、25日、50日、75日、200日移動平均線
              go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma5"], name="MA5", line={"color": "blue", "width": 1.4}),
              go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma25"], name="MA25", line={"color": "green", "width": 1.4}),
              go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma50"], name="MA50", line={"color": "red", "width": 1.4}),
              go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma75"], name="MA75", line={"color": "gray", "width": 1.4}),
              go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma200"], name="MA200", line={"color": "black", "width": 1.4}),

              go.Scatter(x=crossing_dates, y=rdf.loc[crossing_dates, 'ma5'],
                                mode='markers', marker=dict(color='purple', symbol='circle', size=20),
                                name='MA5 crosses above MA50'),

              # MACD
              go.Scatter(yaxis="y2", x=rdf.index ,y=rdf["macd"], name= "macd", line={ "color": "magenta", "width": 1 } ),
              go.Scatter(yaxis="y2", x=rdf.index ,y=rdf["macd_signal"], name= "signal", line={ "color": "green", "width": 1 } ),
              go.Bar(yaxis="y2", x=rdf.index, y=rdf["hist"], name= "histgram", marker={ "color": "slategray" } ) ,

              go.Scatter(yaxis="y2", x=macd_above_dates, y=rdf.loc[macd_above_dates, 'macd'], mode='markers', marker=dict(color='red', symbol='circle', size=10), name='MACD crosses above Signal'),
              go.Scatter(yaxis="y2", x=macd_below_dates, y=rdf.loc[macd_below_dates, 'macd'], mode='markers', marker=dict(color='black', symbol='x', size=10), name='MACD crosses below Signal'),

              # RSI
              go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["rsi14"], name= "RSI14",line={ "color": "magenta", "width": 1 } ),
              go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["rsi28"], name= "RSI28",line={ "color": "green", "width": 1 } ),
              go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["20"], name= "20",line={ "color": "black", "width": 0.5 } ),
              go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["80"], name= "80",line={ "color": "black", "width": 0.5 } ),

              # 出来高
              go.Bar(yaxis="y4", x=rdf.index, y=rdf["Volume"], name= "Volume", marker={ "color": "slategray" } )
          ]

##############################################################
  fig = go.Figure(layout = go.Layout(layout), data = data)
  fig.update_layout({
    "xaxis":{
        "tickvals": rdf.index[::2],
        "ticktext": ["{}-{}".format(x.split("-")[0], x.split("-")[1]) for x in rdf.index[::2]]
        }
  })
  fig.show()

##############################################################
# GUIの作成
root = tk.Tk()
root.title("株価データ分析")

# ラベル
label_code = tk.Label(root, text="株価コード:")
label_code.grid(row=0, column=0)
label_date = tk.Label(root, text="日付(YYYY,MM,DD):")
label_date.grid(row=1, column=0)

# 入力フィールド
entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)
entry_date = tk.Entry(root)
entry_date.grid(row=1, column=1)

# 実行ボタン
execute_button = tk.Button(root, text="実行", command=on_click_execute)
execute_button.grid(row=2, columnspan=2)

root.mainloop()