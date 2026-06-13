"""
Personal Financial Dashboard — Phase 2
Built by: Becky Lin (github.com/blktx)

Run with: streamlit run /Users/beckylin/Desktop/2026/Financial Enginner/dashboard.py
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Becky's Financial Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Load data from SQLite ─────────────────────────────────────────
DB_PATH = "/Users/beckylin/Desktop/2026/Financial Enginner/financial.db"

@st.cache_data(ttl=3600)  # cache for 1 hour, refreshes automatically
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM stocks", conn)
    div = pd.read_sql("SELECT * FROM dividends", conn)
    conn.close()
    return df, div

df, div = load_data()

# ── Sidebar navigation ────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/stock-market.png", width=60)
st.sidebar.title("📊 Financial Dashboard")
st.sidebar.caption("github.com/blktx")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview",
     "🔍 Stock Screener",
     "💰 Dividend Dashboard",
     "🏭 Sector Analysis",
     "📈 Trend & Momentum"],
)

st.sidebar.markdown("---")
st.sidebar.caption(f"📦 {len(df)} stocks tracked")
st.sidebar.caption(f"🔄 Last updated: {df['last_updated'].max()}")


# ════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.title("📊 Personal Financial Dashboard")
    st.caption("Built by Becky Lin · github.com/blktx · Phase 2 of 4")
    st.markdown("---")

    # Top KPI row
    col1, col2, col3, col4, col5 = st.columns(5)

    growth  = df[df["group_type"] == "Growth"]
    divs    = df[df["group_type"] == "Dividend"]
    uptrend = df[df["price_vs_ma50"] > 0] if "price_vs_ma50" in df.columns else pd.DataFrame()
    safe_div = df[
        (df["group_type"] == "Dividend") &
        (df["payout_ratio"] < 60) &
        (df["free_cash_flow_b"] > 0)
    ] if "payout_ratio" in df.columns else pd.DataFrame()

    col1.metric("Total Stocks",     len(df))
    col2.metric("Growth Stocks",    len(growth))
    col3.metric("Dividend Stocks",  len(divs))
    col4.metric("In Uptrend",       len(uptrend))
    col5.metric("Safe Dividends",   len(safe_div))

    st.markdown("---")

    # Two summary tables side by side
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("🚀 Top Growth Stocks by Market Cap")
        top_growth = growth[["ticker","company","price","pe_ratio","market_cap_b"]]\
            .sort_values("market_cap_b", ascending=False)\
            .head(10)\
            .reset_index(drop=True)
        top_growth.columns = ["Ticker","Company","Price","P/E","Mkt Cap ($B)"]
        st.dataframe(top_growth, use_container_width=True, hide_index=True)

    with col_r:
        st.subheader("💰 Top Dividend Stocks by Yield")
        top_div = divs[["ticker","company","price","dividend_yield","payout_ratio"]]\
            .sort_values("dividend_yield", ascending=False)\
            .head(10)\
            .reset_index(drop=True)
        top_div.columns = ["Ticker","Company","Price","Yield %","Payout %"]
        st.dataframe(top_div, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Growth vs Dividend comparison bar chart
    st.subheader("📊 Growth vs Dividend — At a Glance")
    summary = df.groupby("group_type").agg(
        Avg_Price    = ("price", "mean"),
        Avg_PE       = ("pe_ratio", "mean"),
        Avg_Yield    = ("dividend_yield", "mean"),
        Avg_Margin   = ("profit_margin", "mean"),
    ).reset_index()
    summary.columns = ["Group","Avg Price","Avg P/E","Avg Yield %","Avg Margin %"]

    fig = go.Figure()
    metrics = ["Avg P/E", "Avg Yield %", "Avg Margin %"]
    colors  = ["#3C3489", "#085041", "#0C447C"]
    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Bar(
            name=metric,
            x=summary["Group"],
            y=summary[metric].round(1),
            marker_color=color,
            text=summary[metric].round(1),
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE 2 — STOCK SCREENER
# ════════════════════════════════════════════════════════════════
elif page == "🔍 Stock Screener":
    st.title("🔍 Stock Screener")
    st.caption("Filter all 40 stocks by group, sector, yield, and P/E")
    st.markdown("---")

    # Filters row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        group_filter = st.selectbox(
            "Group",
            ["All", "Growth", "Dividend"]
        )
    with col2:
        sectors = ["All"] + sorted(df["sector"].dropna().unique().tolist())
        sector_filter = st.selectbox("Sector", sectors)

    with col3:
        min_yield = st.slider("Min Dividend Yield %", 0.0, 15.0, 0.0, 0.5)

    with col4:
        max_pe = st.slider("Max P/E Ratio", 0, 500, 500, 10)

    # Apply filters
    filtered = df.copy()
    if group_filter != "All":
        filtered = filtered[filtered["group_type"] == group_filter]
    if sector_filter != "All":
        filtered = filtered[filtered["sector"] == sector_filter]
    filtered = filtered[filtered["dividend_yield"] >= min_yield]
    filtered = filtered[
        (filtered["pe_ratio"].isna()) | (filtered["pe_ratio"] <= max_pe)
    ]

    st.markdown(f"**{len(filtered)} stocks match your filters**")

    # Results table
    display_cols = ["ticker","company","sector","group_type",
                    "price","pe_ratio","eps","dividend_yield","market_cap_b"]
    available = [c for c in display_cols if c in filtered.columns]
    result = filtered[available].sort_values("market_cap_b", ascending=False)\
                                .reset_index(drop=True)
    result.columns = [c.replace("_"," ").title() for c in result.columns]
    st.dataframe(result, use_container_width=True, hide_index=True)

    # Scatter plot: P/E vs Yield
    st.markdown("---")
    st.subheader("P/E Ratio vs Dividend Yield")
    scatter_df = filtered.dropna(subset=["pe_ratio","dividend_yield"])
    if not scatter_df.empty:
        fig = px.scatter(
            scatter_df,
            x="pe_ratio",
            y="dividend_yield",
            color="group_type",
            size="market_cap_b",
            hover_name="ticker",
            hover_data=["company","sector","price"],
            color_discrete_map={"Growth":"#3C3489","Dividend":"#085041"},
            labels={"pe_ratio":"P/E Ratio","dividend_yield":"Dividend Yield %",
                    "group_type":"Group","market_cap_b":"Mkt Cap ($B)"},
            height=420,
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE 3 — DIVIDEND DASHBOARD
# ════════════════════════════════════════════════════════════════
elif page == "💰 Dividend Dashboard":
    st.title("💰 Dividend Dashboard")
    st.caption("Yield, payout ratio, safety ratings, and streak analysis")
    st.markdown("---")

    div_df = df[df["group_type"] == "Dividend"].copy()

    # Safety rating function
    def safety_rating(row):
        if pd.isna(row.get("payout_ratio")) or row.get("dividend_yield", 0) == 0:
            return "No Dividend"
        if row["payout_ratio"] < 60 and row.get("free_cash_flow_b", 0) > 0 \
                and row.get("dividend_streak", 0) >= 5:
            return "✅ Safe"
        if row["payout_ratio"] < 80 and row.get("free_cash_flow_b", 0) > 0:
            return "⚠️ Moderate"
        return "🔴 At Risk"

    div_df["Safety"] = div_df.apply(safety_rating, axis=1)

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Yield",      f"{div_df['dividend_yield'].mean():.1f}%")
    c2.metric("Avg Payout",     f"{div_df['payout_ratio'].mean():.1f}%")
    c3.metric("Safe Dividends", len(div_df[div_df["Safety"] == "✅ Safe"]))
    c4.metric("Avg Streak",     f"{div_df['dividend_streak'].mean():.0f} yrs"
              if "dividend_streak" in div_df.columns else "—")

    st.markdown("---")

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.subheader("Dividend Yield by Stock")
        bar_df = div_df.sort_values("dividend_yield", ascending=True)
        fig = px.bar(
            bar_df,
            x="dividend_yield",
            y="ticker",
            orientation="h",
            color="dividend_yield",
            color_continuous_scale=["#E1F5EE","#085041"],
            text=bar_df["dividend_yield"].round(1).astype(str) + "%",
            labels={"dividend_yield":"Yield %","ticker":""},
            height=520,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(l=10, r=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Safety Ratings")
        safety_table = div_df[["ticker","company","dividend_yield",
                                "payout_ratio","dividend_streak","Safety"]]\
            .sort_values("dividend_yield", ascending=False)\
            .reset_index(drop=True)
        safety_table.columns = ["Ticker","Company","Yield %",
                                  "Payout %","Streak","Safety"]
        st.dataframe(safety_table, use_container_width=True,
                     hide_index=True, height=520)

    # Payout ratio chart
    st.markdown("---")
    st.subheader("Payout Ratio — How Much of Earnings Go to Dividends?")
    st.caption("Under 60% = sustainable   |   Over 80% = watch carefully")
    payout_df = div_df.dropna(subset=["payout_ratio"])\
                      .sort_values("payout_ratio", ascending=False)

    colors = ["#A32D2D" if p > 80 else "#BA7517" if p > 60 else "#085041"
              for p in payout_df["payout_ratio"]]
    fig2 = go.Figure(go.Bar(
        x=payout_df["ticker"],
        y=payout_df["payout_ratio"],
        marker_color=colors,
        text=payout_df["payout_ratio"].round(0).astype(int).astype(str) + "%",
        textposition="outside",
    ))
    fig2.add_hline(y=60, line_dash="dash", line_color="#085041",
                   annotation_text="60% — Safe threshold")
    fig2.add_hline(y=80, line_dash="dash", line_color="#A32D2D",
                   annotation_text="80% — Watch threshold")
    fig2.update_layout(
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Payout Ratio %",
        margin=dict(t=40),
    )
    st.plotly_chart(fig2, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE 4 — SECTOR ANALYSIS
# ════════════════════════════════════════════════════════════════
elif page == "🏭 Sector Analysis":
    st.title("🏭 Sector Analysis")
    st.caption("Concentration risk, valuations, and returns by sector")
    st.markdown("---")

    sector_df = df.groupby(["sector","group_type"]).agg(
        Num_Stocks    = ("ticker",          "count"),
        Avg_PE        = ("pe_ratio",        "mean"),
        Avg_Yield     = ("dividend_yield",  "mean"),
        Avg_Margin    = ("profit_margin",   "mean"),
        Total_Cap     = ("market_cap_b",    "sum"),
    ).reset_index()
    sector_df = sector_df.round(2)

    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("Market Cap by Sector")
        total_by_sector = df.groupby("sector")["market_cap_b"].sum().reset_index()
        fig = px.pie(
            total_by_sector.dropna(subset=["sector"]),
            names="sector",
            values="market_cap_b",
            color_discrete_sequence=px.colors.qualitative.Set2,
            height=380,
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Avg P/E by Sector")
        pe_sector = df.groupby("sector")["pe_ratio"].mean()\
                      .dropna().sort_values(ascending=False).reset_index()
        fig2 = px.bar(
            pe_sector,
            x="pe_ratio",
            y="sector",
            orientation="h",
            color="pe_ratio",
            color_continuous_scale=["#E1F5EE","#3C3489"],
            text=pe_sector["pe_ratio"].round(1),
            labels={"pe_ratio":"Avg P/E","sector":""},
            height=380,
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Full sector table
    st.markdown("---")
    st.subheader("Full Sector Breakdown")
    display = sector_df.sort_values("Total_Cap", ascending=False)\
                       .reset_index(drop=True)
    display.columns = ["Sector","Group","# Stocks","Avg P/E",
                        "Avg Yield %","Avg Margin %","Total Mkt Cap ($B)"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    # Avg yield by sector — dividend stocks only
    st.markdown("---")
    st.subheader("Avg Dividend Yield by Sector")
    yield_sector = df[df["group_type"]=="Dividend"]\
        .groupby("sector")["dividend_yield"].mean()\
        .dropna().sort_values(ascending=False).reset_index()
    fig3 = px.bar(
        yield_sector,
        x="sector",
        y="dividend_yield",
        color="dividend_yield",
        color_continuous_scale=["#E1F5EE","#085041"],
        text=yield_sector["dividend_yield"].round(1).astype(str) + "%",
        labels={"dividend_yield":"Avg Yield %","sector":""},
        height=360,
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(t=20),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# PAGE 5 — TREND & MOMENTUM
# ════════════════════════════════════════════════════════════════
elif page == "📈 Trend & Momentum":
    st.title("📈 Trend & Momentum")
    st.caption("52-week range, moving averages, and momentum signals")
    st.markdown("---")

    trend_df = df.copy()

    # Signal logic
    def trend_signal(row):
        ma50  = row.get("price_vs_ma50")
        price = row.get("price", 0)
        ma200 = row.get("ma_200")
        if pd.isna(ma50):
            return "No Data"
        if ma50 > 0 and not pd.isna(ma200) and price > ma200:
            return "Strong Uptrend"
        if ma50 > 0:
            return "Short Uptrend"
        if ma50 < 0 and not pd.isna(ma200) and price < ma200:
            return "Downtrend"
        return "Mixed"

    trend_df["Trend"] = trend_df.apply(trend_signal, axis=1)

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Strong Uptrend", len(trend_df[trend_df["Trend"]=="Strong Uptrend"]))
    c2.metric("Short Uptrend",  len(trend_df[trend_df["Trend"]=="Short Uptrend"]))
    c3.metric("Downtrend",      len(trend_df[trend_df["Trend"]=="Downtrend"]))
    c4.metric("Mixed",          len(trend_df[trend_df["Trend"]=="Mixed"]))

    st.markdown("---")

    # Price vs MA50 chart
    st.subheader("Price vs 50-Day Moving Average")
    st.caption("Positive = above MA50 (bullish)   |   Negative = below MA50 (bearish)")

    ma_df = trend_df.dropna(subset=["price_vs_ma50"])\
                    .sort_values("price_vs_ma50", ascending=False)
    colors = ["#085041" if v > 0 else "#A32D2D" for v in ma_df["price_vs_ma50"]]

    fig = go.Figure(go.Bar(
        x=ma_df["ticker"],
        y=ma_df["price_vs_ma50"],
        marker_color=colors,
        text=ma_df["price_vs_ma50"].round(1).astype(str) + "%",
        textposition="outside",
        hovertext=ma_df["company"],
    ))
    fig.add_hline(y=0, line_color="#888888", line_width=1)
    fig.update_layout(
        height=400,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="% vs MA50",
        margin=dict(t=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 52-week range table
    st.markdown("---")
    st.subheader("52-Week Price Range Position")
    st.caption("100% = at 52-week high   |   0% = at 52-week low")

    range_df = trend_df.dropna(subset=["week_52_high","week_52_low"]).copy()
    range_df["Range_Position"] = (
        (range_df["price"] - range_df["week_52_low"]) /
        (range_df["week_52_high"] - range_df["week_52_low"]) * 100
    ).round(1)

    fig2 = px.scatter(
        range_df,
        x="Range_Position",
        y="ticker",
        color="group_type",
        size="market_cap_b",
        hover_name="ticker",
        hover_data=["company","price","week_52_high","week_52_low"],
        color_discrete_map={"Growth":"#3C3489","Dividend":"#085041"},
        labels={"Range_Position":"Position in 52-Wk Range %",
                "ticker":"","group_type":"Group"},
        height=600,
    )
    fig2.add_vline(x=50, line_dash="dash", line_color="#AAAAAA")
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Full trend table
    st.markdown("---")
    st.subheader("Full Trend Signal Table")
    tbl = trend_df[["ticker","company","group_type","price",
                     "ma_50","ma_200","price_vs_ma50","Trend"]]\
        .sort_values("price_vs_ma50", ascending=False)\
        .reset_index(drop=True)
    tbl.columns = ["Ticker","Company","Group","Price",
                   "MA50","MA200","% vs MA50","Trend"]
    st.dataframe(tbl, use_container_width=True, hide_index=True)
