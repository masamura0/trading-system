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
def get_us_stock_data(symbol):
    df = yf.download(symbol, start="2020-01-01", end=datetime.now().strftime("%Y-%m-%d"))
    return df

def get_stock_data(code):
    df = pdr.DataReader("{}.JP".format(code), "stooq").sort_index()
    return df

# ポイント評価用の関数を作成
def calculate_risk_points(rolling_5_days_pct_change, rolling_25_days_pct_change, rolling_50_days_pct_change, rolling_75_days_pct_change, rolling_200_days_pct_change):
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

    # 25日足の条件判定とポイント付与
    if abs(rolling_25_days_pct_change) <= 0.03:
        total_points += 1
    elif abs(rolling_25_days_pct_change) <= 0.06:
        total_points += 2
    elif abs(rolling_25_days_pct_change) <= 0.08:
        total_points += 3
    elif abs(rolling_25_days_pct_change) <= 0.12:
        total_points += 4
    else:
        total_points += 5

    # 50日足の条件判定とポイント付与
    if abs(rolling_50_days_pct_change) <= 0.03:
        total_points += 1
    elif abs(rolling_50_days_pct_change) <= 0.06:
        total_points += 2
    elif abs(rolling_50_days_pct_change) <= 0.08:
        total_points += 3
    elif abs(rolling_50_days_pct_change) <= 0.12:
        total_points += 4
    else:
        total_points += 5

    # 75日足の条件判定とポイント付与
    if abs(rolling_75_days_pct_change) <= 0.03:
        total_points += 1
    elif abs(rolling_75_days_pct_change) <= 0.06:
        total_points += 2
    elif abs(rolling_75_days_pct_change) <= 0.08:
        total_points += 3
    elif abs(rolling_75_days_pct_change) <= 0.12:
        total_points += 4
    else:
        total_points += 5

    # 200日足の条件判定とポイント付与
    if abs(rolling_200_days_pct_change) <= 0.03:
        total_points += 1
    elif abs(rolling_200_days_pct_change) <= 0.06:
        total_points += 2
    elif abs(rolling_200_days_pct_change) <= 0.08:
        total_points += 3
    elif abs(rolling_200_days_pct_change) <= 0.12:
        total_points += 4
    else:
        total_points += 5

    # 総合的なリスク評価を算出
    if total_points <= 5:
        return '低リスク'
    elif total_points <= 10:
        return 'やや低リスク'
    elif total_points <= 15:
        return '中リスク'
    elif total_points <= 20:
        return 'やや高リスク'
    else:
        return '高リスク'

##############################################################
def on_click_execute():
    entered_code = entry_code.get()

    entered_start_date = entry_start_date.get()
    entered_start_date = datetime.strptime(entered_start_date, "%Y,%m,%d")

    # 日付のデフォルト値を現在の日付に設定
    entered_date = datetime.now().strftime("%Y,%m,%d")
    # 日付の入力欄が空でない場合は入力された値を使う
    if entry_date.get() != "":
        entered_date = entry_date.get()
    entered_date = datetime.strptime(entered_date, "%Y,%m,%d")

    # 日本の株の場合
    if entered_code.endswith('.JP'):
        try:
            entered_code = int(entered_code[:-3])
        except ValueError:
            print("有効な株価コードを入力してください")
            return
        df = get_stock_data(entered_code)
    else:  # アメリカの株の場合
        # Yahoo Finance APIを使用して銘柄情報を取得し、存在するかどうかを確認
        try:
            stock = yf.Ticker(entered_code)
            stock_info = stock.info
            if 'country' in stock_info and stock_info['country'] == 'United States':
                df = get_us_stock_data(entered_code)
            else:
                print("有効なアメリカ株価コードを入力してください")
                return
        except ValueError:
            print("有効なアメリカ株価コードを入力してください")
            return

    # データフレームに各期間の変動率を追加
    df['5日間変動率'] = df['Close'].pct_change(periods=5)
    df['25日間変動率'] = df['Close'].pct_change(periods=25)
    df['50日間変動率'] = df['Close'].pct_change(periods=50)
    df['75日間変動率'] = df['Close'].pct_change(periods=75)
    df['200日間変動率'] = df['Close'].pct_change(periods=200)

    # 各期間の変動率を取得
    rolling_5_days_change = df['5日間変動率'].iloc[-1]
    rolling_25_days_change = df['25日間変動率'].iloc[-1]
    rolling_50_days_change = df['50日間変動率'].iloc[-1]
    rolling_75_days_change = df['75日間変動率'].iloc[-1]
    rolling_200_days_change = df['200日間変動率'].iloc[-1]
  

    # ポイントを計算してリスク評価を取得
    risk_evaluation = calculate_risk_points(rolling_5_days_change, rolling_25_days_change, rolling_50_days_change, rolling_75_days_change, rolling_200_days_change)

    # ラベル表示のためにリスク評価を表示
    #    print(f"リスク評価: {risk_evaluation}")    

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
    rdf = df[(df.index >= entered_start_date) & (df.index <= entered_date)]
    rdf.index = pd.to_datetime(rdf.index).strftime("%m-%d-%Y")

##############################################################
    # ma5がma50を上に交差するポイントを見つける
    crossing_points = np.where((rdf['ma5'].shift(1) < rdf['ma50'].shift(1)) & (rdf['ma5'] > rdf['ma50']))[0]

    # グラフのデータを設定する前に、紫のまるいマーカーを追加する
    crossing_dates = rdf.iloc[crossing_points].index

##############################################################
    # 5日移動平均と50日移動平均の関係を判定してトレンドを表示
    trend = ''
    if rdf['ma5'].iloc[-1] > rdf['ma50'].iloc[-1]:
        trend = '上昇トレンド'
    else:
        trend = '下降トレンド'

    # MACD、シグナル、ヒストグラムを算出
    macd, macdsignal, hist = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    df["macd"] = macd
    df["macd_signal"] = macdsignal
    df["hist"] = hist   

    # RSI
    rsi14 = ta.RSI(close, timeperiod=14)
    rsi28 = ta.RSI(close, timeperiod=28)
    df["rsi14"], df["rsi28"] = rsi14, rsi28 
    df["70"],  df["30"] = [70 for _ in close], [30 for _ in close]  

    # ストキャスティクス
    slowK, slowD = ta.STOCH(df["High"], df["Low"], df["Close"],fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df["slowK"], df["slowD"] = slowK, slowD 
    df["80"],  df["20"] = [80 for _ in close], [20 for _ in close]  

    rdf = df[dt.datetime(2020,1,1):dt.datetime(2024,1,13)]
    rdf.index = pd.to_datetime(rdf.index).strftime("%m-%d-%Y")

    # トレンドを表示
    #    print(f"トレンド: {trend}")

    layout = {
        "height": 1000,
        "title": {"text": str(entered_code), "x": 0.5},
        "xaxis": {"rangeslider": {"visible": False}},
        "yaxis1": {"domain": [0.50, 1.0], "title": "価格（円）", "side": "left", "tickformat": ","},
        "yaxis2": { "domain": [.30, .395], "title": "MACD", "side": "right"}, # MACD
        "yaxis3": { "domain": [.20, .295], "title": "RSI", "side": "right"}, # RSI
        "yaxis4": { "domain": [.10, .195], "title": "STC", "side": "right"}, # ストキャスティクス
        "yaxis5": { "domain": [.00, .095], "title": "Volume", "side": "right"}, # 出来高
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
                # MACD
                go.Scatter(yaxis="y2" ,x=rdf.index ,y=rdf["macd"], name= "macd", line={ "color": "magenta", "width": 1 } ),
                go.Scatter(yaxis="y2" ,x=rdf.index ,y=rdf["macd_signal"], name= "signal", line={ "color": "green", "width": 1 } ),
                go.Bar(yaxis="y2" ,x=rdf.index, y=rdf["hist"], name= "histgram", marker={ "color": "slategray" } ) ,

                # RSI
                go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["rsi14"], name= "RSI14",line={ "color": "magenta", "width": 1 } ),
                go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["rsi28"], name= "RSI28",line={ "color": "green", "width": 1 } ),
                go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["30"], name= "30",line={ "color": "black", "width": 0.5 } ),
                go.Scatter(yaxis="y3" ,x=rdf.index ,y=rdf["70"], name= "70",line={ "color": "black", "width": 0.5 } ),  

                # ストキャスティクス
                go.Scatter(yaxis="y4" ,x=rdf.index ,y=rdf["slowK"], name= "slowK",line={ "color": "magenta", "width": 1 } ),
                go.Scatter(yaxis="y4" ,x=rdf.index ,y=rdf["slowD"], name= "slowD",line={ "color": "green", "width": 1 } ),
                go.Scatter(yaxis="y4" ,x=rdf.index ,y=rdf["20"], name= "20",line={ "color": "black", "width": 0.5 } ),
                go.Scatter(yaxis="y4" ,x=rdf.index ,y=rdf["80"], name= "80",line={ "color": "black", "width": 0.5 } ), 
                 
                # 出来高
                go.Bar(yaxis="y5", x=rdf.index, y=rdf["Volume"], name= "Volume", marker={ "color": "slategray" } )
            ]   
    
##############################################################
    fig = go.Figure(layout = go.Layout(layout), data = data)

    # ticktextを生成する処理を追加
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

    # 注釈を作成して、リスクを表示
    fig.add_annotation(
        x=1,  # x座標（1は右端）
        y=1,  # y座標（1は上端）
        xref="paper",
        yref="paper",
        text=f"リスク評価: {risk_evaluation}",  # リスク評価を表示するテキスト1
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
        x=0.86,  # x座標（1は右端）
        y=1,  # y座標（0.9は上から少し下の位置）
        xref="paper",
        yref="paper",
        text=f"トレンド: {trend}",  # トレンドを表示するテキスト2
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

# ラベル
label_code = tk.Label(root, text="株価コード:")
label_code.grid(row=0, column=0)

label_date = tk.Label(root, text="いつから(YYYY,MM,DD):")
label_date.grid(row=1, column=0)

label_date = tk.Label(root, text="いつまで(YYYY,MM,DD):")
label_date.grid(row=2, column=0)

# ペースト機能を有効にするためにEntryウィジェットにバインディングを追加
entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)
entry_code.bind("<Button-3>", lambda e: paste_text(entry_code))  # 右クリックでペーストできるように設定

entry_date = tk.Entry(root)
entry_date.grid(row=1, column=1)
entry_date.bind("<Button-3>", lambda e: paste_text(entry_date))  # 右クリックでペーストできるように設定

entry_date = tk.Entry(root)
entry_date.grid(row=2, column=1)
entry_date.bind("<Button-3>", lambda e: paste_text(entry_date))  # 右クリックでペーストできるように設定

# 入力フィールド
entry_code = tk.Entry(root)
entry_code.grid(row=0, column=1)

entry_start_date = tk.Entry(root)
entry_start_date.grid(row=1, column=1)
entry_start_date.insert(0, "2020,01,01") # デフォルトで2020年1月1日からの日付を挿入

entry_date = tk.Entry(root)
entry_date.grid(row=2, column=1)
entry_date.insert(0, datetime.now().strftime("%Y,%m,%d"))  # 現在の日付を3番目の入力フィールドに挿入

# 実行ボタン
execute_button = tk.Button(root, text="実行", command=on_click_execute)
execute_button.grid(row=3, columnspan=3)

# Tkinter main loop
root.mainloop()





