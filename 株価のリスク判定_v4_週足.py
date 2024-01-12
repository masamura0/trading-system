import pandas_datareader.data as pdr
import plotly.graph_objs as go
import talib as ta
import datetime as dt
import pandas as pd
import numpy as np
import tkinter as tk
from datetime import datetime
import yfinance as yf

##############################################################
def get_us_stock_data_weekly(symbol):
    df = yf.download(symbol, start="2020-01-01", end=datetime.now().strftime("%Y-%m-%d"), interval="1wk")
    return df

def get_stock_data_weekly(code):
    df = pdr.DataReader("{}.JP".format(code), "stooq", start="2020-01-01").resample('W-Mon').last()
    return df

# ポイント評価用の関数を作成
def calculate_risk_points(ma_changes):
    total_points = 0

    # Iterate through the weekly moving average changes
    for ma_change in ma_changes:
        # 低リスク
        if abs(ma_change) <= 0.03:
            total_points += 1
        # やや低リスク
        elif abs(ma_change) <= 0.06:
            total_points += 2
        # 中リスク
        elif abs(ma_change) <= 0.08:
            total_points += 3
        # やや高リスク
        elif abs(ma_change) <= 0.12:
            total_points += 4
        # 高リスク
        else:
            total_points += 5

    # Calculate the average risk points
    average_points = total_points / len(ma_changes)

    # Determine the risk level
    if average_points <= 1:
        return '低リスク'
    elif average_points <= 2:
        return 'やや低リスク'
    elif average_points <= 3:
        return '中リスク'
    elif average_points <= 4:
        return 'やや高リスク'
    else:
        return '高リスク'

##############################################################
def on_click_execute():
    entered_code = entry_code.get()

    entered_start_date = entry_start_date.get()
    entered_start_date = datetime.strptime(entered_start_date, "%Y,%m,%d")

    entered_date = datetime.now().strftime("%Y,%m,%d")
    if entry_date.get() != "":
        entered_date = entry_date.get()
    entered_date = datetime.strptime(entered_date, "%Y,%m,%d")

    if entered_code.endswith('.JP'):
        try:
            entered_code = int(entered_code[:-3])
        except ValueError:
            print("有効な株価コードを入力してください")
            return
        df = get_stock_data_weekly(entered_code)
    else:
        try:
            stock = yf.Ticker(entered_code)
            stock_info = stock.info
            if 'country' in stock_info and stock_info['country'] == 'United States':
                df = get_us_stock_data_weekly(entered_code)
            else:
                print("有効なアメリカ株価コードを入力してください")
                return
        except ValueError:
            print("有効なアメリカ株価コードを入力してください")
            return

    df['9週足変動率'] = df['Close'].pct_change(periods=9)
    df['13週足変動率'] = df['Close'].pct_change(periods=13)
    df['26週足変動率'] = df['Close'].pct_change(periods=26)

    rolling_9_weeks_change = df['9週足変動率'].iloc[-1]
    rolling_13_weeks_change = df['13週足変動率'].iloc[-1]
    rolling_26_weeks_change = df['26週足変動率'].iloc[-1]

    ma_changes = [rolling_9_weeks_change, rolling_13_weeks_change, rolling_26_weeks_change]
    risk_evaluation = calculate_risk_points(ma_changes)

    close = df["Close"]

##############################################################
    ma9 = ta.SMA(close, timeperiod=9)
    df["ma9"] = ma9
    ma13 = ta.SMA(close, timeperiod=13)
    df["ma13"] = ma13
    ma26 = ta.SMA(close, timeperiod=26)
    df["ma26"] = ma26

##############################################################
    rdf = df[(df.index >= entered_start_date) & (df.index <= entered_date)]
    rdf.index = pd.to_datetime(rdf.index).strftime("%m-%d-%Y")

##############################################################
    crossing_points = np.where((rdf['ma9'].shift(1) < rdf['ma13'].shift(1)) & (rdf['ma9'] > rdf['ma13']))[0]

    crossing_dates = rdf.iloc[crossing_points].index

##############################################################
    trend = ''
    if rdf['ma9'].iloc[-1] > rdf['ma13'].iloc[-1]:
        trend = '上昇トレンド'
    else:
        trend = '下降トレンド'

    layout = {
        "height": 1000,
        "title": {"text": str(entered_code), "x": 0.5},
        "xaxis": {"rangeslider": {"visible": False}},
        "yaxis1": {"domain": [0.46, 1.0], "title": "価格（円）", "side": "left", "tickformat": ","},
        "plot_bgcolor": "lightblue",
    }   

##############################################################
    data =  [
                go.Candlestick(yaxis="y1", x=rdf.index, open=rdf["Open"], high=rdf["High"], low=rdf["Low"], close=rdf["Close"],
                                increasing_line_color="red", decreasing_line_color="gray"), 
                go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma9"], name="MA9", line={"color": "blue", "width": 1.4}),
                go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma13"], name="MA13", line={"color": "green", "width": 1.4}),
                go.Scatter(yaxis="y1", x=rdf.index, y=rdf["ma26"], name="MA26", line={"color": "red", "width": 1.4}),
                go.Scatter(x=crossing_dates, y=rdf.loc[crossing_dates, 'ma9'],
                                  mode='markers', marker=dict(color='purple', symbol='circle', size=10),
                                  name='MA9 crosses above MA13'),
            ]   
    
##############################################################
    fig = go.Figure(layout = go.Layout(layout), data = data)

    ticktext = []
    first_date = rdf.index[0]
    first_date_year_month = datetime.strptime(first_date, "%m-%d-%Y").strftime("%Y年%m月")
    ticktext.append(first_date_year_month)

    for date in rdf.index[1:]:
        month_only = datetime.strptime(date, "%m-%d-%Y").strftime("%m月")
        if month_only not in ticktext:
            ticktext.append(month_only)

    fig.update_layout({
        "xaxis":{
            "tickvals": rdf.index[::2],
            "ticktext": ticktext
        }
    })

    fig.add_annotation(
        x=1,
        y=1,
        xref="paper",
        yref="paper",
        text=f"リスク評価: {risk_evaluation}",
        showarrow=False,
        font=dict(
            family="Arial",
            size=12,
            color="black"
        ),
        bgcolor="lightgray",
        bordercolor="black",
        borderwidth=1,
        borderpad=10,
        opacity=0.8
    )

    fig.add_annotation(
        x=0.86,
        y=1,
        xref="paper",
        yref="paper",
        text=f"トレンド: {trend}",
        showarrow=False,
        font=dict(
            family="Arial",
            size=12,
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

label_code = tk.Label(root, text="株価コード:")
label_code.grid(row=0, column=0)

label_date = tk.Label(root, text="いつから(YYYY,MM,DD):")
label_date.grid(row=1, column=0)

label_date = tk.Label(root, text="いつまで(YYYY,MM,DD):")
label_date.grid(row=2, column=0)

entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)
entry_code.bind("<Button-3>", lambda e: paste_text(entry_code))

entry_date = tk.Entry(root)
entry_date.grid(row=1, column=1)
entry_date.bind("<Button-3>", lambda e: paste_text(entry_date))

entry_date = tk.Entry(root)
entry_date.grid(row=2, column=1)
entry_date.bind("<Button-3>", lambda e: paste_text(entry_date))

entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)

entry_start_date = tk.Entry(root)
entry_start_date.grid(row=1, column=1)
entry_start_date.insert(0, "2020,01,01")

entry_date = tk.Entry(root)
entry_date.grid(row=2, column=1)
entry_date.insert(0, datetime.now().strftime("%Y,%m,%d"))

execute_button = tk.Button(root, text="実行", command=on_click_execute)
execute_button.grid(row=3, columnspan=3)

root.mainloop()