import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

# アプリのタイトルを設定
st.title('米国株価可視化アプリ')

# サイドバーに説明文を表示
st.sidebar.write("""
# GAFA株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

# スライダーを使用して表示日数を選択
days = st.sidebar.slider('日数', 1, 50, 20)

# 選択された日数を表示
st.write(f"""
### 過去 **{days}日間** のGAFA株価
""")

# 株価データを取得する関数を定義（キャッシュを使用）
@st.cache_resource
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        try:
            tkr = yf.Ticker(tickers[company])
            hist = tkr.history(period=f'{days}d')
            hist.index = hist.index.strftime('%d %B %Y')
            hist = hist[['Close']]
            hist.columns = [company]
            hist = hist.T
            hist.index.name = 'Name'
            df = pd.concat([df, hist])
        except:
            st.error(f"エラー： {company} のデータを取得できませんでした。")
    return df

try: 
    # サイドバーに株価の範囲を設定するセクションを表示
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    
    # 最小値と最大値を設定するスライダーを表示
    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください。',
        0.0, 3500.0, (0.0, 3500.0)
    )

    # 対象となるGAFA企業のティッカーシンボルを定義
    tickers = {
        'apple': 'AAPL',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    # 株価データを取得
    df = get_data(days, tickers)
    
    # ユーザーが選択した企業の複数選択セレクトボックスを表示
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['google', 'amazon']
    )

    # 企業が選択されている場合
    if not companies:
        st.error('少なくとも一社は選んでください。')
    else:
        # 選択された企業の株価データを表示
        data = df.loc[companies]
        st.write("### 株価 (USD)", data.sort_index())
        
        # データの準備と可視化
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        # 可視化を表示
        st.altair_chart(chart, use_container_width=True)
        
# エラーが発生した場合の処理
except Exception as e:
    st.error(f"おっと！なにかエラーが起きているようです。エラー詳細: {e}")
