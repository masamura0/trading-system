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

# ポイント評価用の関数を作成
def calculate_risk_points(rolling_5_days_pct_change):
    total_points = 0

    # 5日足の条件判定とポイント付与
    if abs(rolling_5_days_pct_change) <= 0.03:
        total_points += 1
    elif abs(rolling_5_days_pct_change) <= 0.06:
        total_points += 2
    elif abs(rolling_5_days_pct_change) <= 0.08:
        total_points += 3
    elif abs(rolling_5_days_pct_change) <= 0.12:
        total_points += 4
    else:
        total_points += 5

    # 総合的なリスク評価を算出
    if total_points <= 1:
        return '低リスク'
    elif total_points <= 2:
        return 'やや低リスク'
    elif total_points <= 3:
        return 'やや低リスク'
    elif total_points <= 4:
        return 'やや低リスク'
    else:
        return '高リスク'

##############################################################
def on_click_execute():
    entered_code = int(entry_code.get())
    entered_date = entry_date.get()
    entered_date = datetime.strptime(entered_date, "%Y,%m,%d")

    # データフレームを取得
    df = get_stock_data(entered_code)

    # データフレームに各期間の変動率を追加
    df['5日間変動率'] = df['Close'].pct_change(periods=5)

    # 各期間の変動率を取得
    rolling_5_days_change = df['5日間変動率'].iloc[-1]
  

    # ポイントを計算してリスク評価を取得
    risk_evaluation = calculate_risk_points(rolling_5_days_change)

    # ラベル表示のためにリスク評価を表示
    print(f"リスク評価: {risk_evaluation}")    

    df = get_stock_data(entered_code)
    close = df["Close"]

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

##############################################################
    rdf = df[dt.datetime(2020,1,1):dt.datetime(entered_date.year, entered_date.month, entered_date.day)]
    rdf.index = pd.to_datetime(rdf.index).strftime("%m-%d-%Y")

##############################################################
    # ma5がma50を上に交差するポイントを見つける
    crossing_points = np.where((rdf['ma5'].shift(1) < rdf['ma50'].shift(1)) & (rdf['ma5'] > rdf['ma50']))[0]

    # グラフのデータを設定する前に、紫のまるいマーカーを追加する
    crossing_dates = rdf.iloc[crossing_points].index

##############################################################
    layout = {
        "height": 1000,
        "title": {"text": str(entered_code), "x": 0.5},
        "xaxis": {"rangeslider": {"visible": False}},
        "yaxis1": {"domain": [0.46, 1.0], "title": "価格（円）", "side": "left", "tickformat": ","},
        "plot_bgcolor": "lightblue",
    }   

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
                                  mode='markers', marker=dict(color='purple', symbol='circle', size=10),
                                  name='MA5 crosses above MA50'),
            ]   
    
##############################################################
    fig = go.Figure(layout = go.Layout(layout), data = data)
    fig.update_layout({
      "xaxis":{
          "tickvals": rdf.index[::2],
          "ticktext": ["{}-{}".format(x.split("-")[0], x.split("-")[1]) for x in rdf.index[::2]]
          }
    })

    # 注釈を作成して、リスクを表示
    fig.add_annotation(
        x=1,  # x座標（1は右端）
        y=1,  # y座標（1は上端）
        xref="paper",
        yref="paper",
        text=f"リスク評価: {risk_evaluation}",  # 表示するテキスト
        showarrow=False,
        font=dict(
            family="Arial",
            size=14,
            color="black"
        ),
        bgcolor="lightgray",
        bordercolor="black",
        borderwidth=1,
        borderpad=10,
        opacity=0.8
    )   
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

# ペースト機能を有効にするためにEntryウィジェットにバインディングを追加
entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)
entry_code.bind("<Button-3>", lambda e: paste_text(entry_code))  # 右クリックでペーストできるように設定

entry_date = tk.Entry(root)
entry_date.grid(row=1, column=1)
entry_date.bind("<Button-3>", lambda e: paste_text(entry_date))  # 右クリックでペーストできるように設定

# 入力フィールド
entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)
entry_date = tk.Entry(root)
entry_date.grid(row=1, column=1)

# 実行ボタン
execute_button = tk.Button(root, text="実行", command=on_click_execute)
execute_button.grid(row=2, columnspan=2)

root.mainloop()