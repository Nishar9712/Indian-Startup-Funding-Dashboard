import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    layout='wide',
    page_title='Indian Startup Funding Analysis'
)

# Apply Seaborn style
sns.set_theme(style='whitegrid')

# Disable scientific notation globally in Matplotlib
plt.rcParams['axes.formatter.useoffset'] = False
plt.rcParams['axes.formatter.limits'] = [-99, 99]

# Data Loading & Processing
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('Cleaned Startup funding.csv')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month
    df['month_name'] = df['Date'].dt.strftime('%b')
    
    # Column mapping
    df['amount'] = df['Investment Amount($)']
    df['startup'] = df['Startup']
    df['industry'] = df['Industry']
    df['sub_vertical'] = df['Sub Vertical']
    df['city'] = df['City']
    df['investors'] = df['Investors']
    df['investment_type'] = df['Investment Type']
    
    return df

df = load_data()

# Helper Functions
# ---------------------------------------------------------
def format_currency(val):
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    elif val >= 1e6:
        return f"${val / 1e6:.2f}M"
    elif val >= 1e3:
        return f"${val / 1e3:.1f}K"
    else:
        return f"${val:,.0f}"

def extract_investors():
    investors_set = set()
    for item in df['investors'].dropna():
        for inv in str(item).split(','):
            clean_inv = inv.strip()
            if clean_inv and clean_inv.lower() not in ['undisclosed investors', 'undisclosed', '']:
                investors_set.add(clean_inv)
    return sorted(list(investors_set))

def get_top_n_series(series, n=5):
    """Groups a pandas Series to keep top N categories and combine remaining into 'Others'."""
    series = series[series > 0].sort_values(ascending=False)
    if len(series) > n:
        top_part = series.iloc[:n]
        others_sum = series.iloc[n:].sum()
        if others_sum > 0:
            top_part = pd.concat([top_part, pd.Series({'Others': others_sum})])
        return top_part
    return series

# Sidebar Navigation
# ---------------------------------------------------------
st.sidebar.title("Startup Funding Dashboard")
option = st.sidebar.selectbox("Select View", ["Overall Analysis", "StartUp", "Investor"])

# 1. OVERALL ANALYSIS
# ---------------------------------------------------------
def load_overall_analysis():
    st.title("Overall Analysis")

    # Metrics calculation
    total_amount = df['amount'].sum()
    max_funding = df['amount'].max()
    max_startup = df.loc[df['amount'].idxmax()]['startup']
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    num_startups = df['startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Funding", format_currency(total_amount))
    with col2:
        st.metric("Max Funding", format_currency(max_funding), f"Startup: {max_startup}")
    with col3:
        st.metric("Avg Funding", format_currency(avg_funding))
    with col4:
        st.metric("Funded Startups", f"{num_startups:,}")

    st.write("---")

    # MoM Graph
    st.header("Month-on-Month (MoM) Trend")
    selected_option = st.selectbox("Select Metric", ["Total Amount ($ Millions)", "Count of Deals"])
    
    mom_df = df.groupby(['year', 'month']).agg(
        total_amount=('amount', 'sum'),
        deal_count=('amount', 'count')
    ).reset_index()
    mom_df['x_axis'] = mom_df['month'].astype(str).str.zfill(2) + '-' + mom_df['year'].astype(str)
    mom_df = mom_df.sort_values(['year', 'month'])
    mom_df['amount_m'] = mom_df['total_amount'] / 1e6

    target_metric = 'amount_m' if selected_option == "Total Amount ($ Millions)" else 'deal_count'
    y_label = "Funding Amount ($ Millions)" if selected_option == "Total Amount ($ Millions)" else "Number of Deals"

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=mom_df, x='x_axis', y=target_metric, marker='o', color='#1f77b4', ax=ax, linewidth=2)
    ax.set_title(f"MoM {selected_option} Trend", fontsize=12, fontweight='bold')
    ax.set_xlabel("Month-Year")
    ax.set_ylabel(y_label)
    ax.ticklabel_format(style='plain', axis='y', useOffset=False)
    
    ticks_to_show = range(0, len(mom_df), max(1, len(mom_df) // 12))
    ax.set_xticks(ticks_to_show)
    ax.set_xticklabels(mom_df['x_axis'].iloc[ticks_to_show], rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

    st.write("---")

    # Sector Analysis (Pie & Bar options)
    st.header("Sector & City Analysis")
    sector_metric_option = st.radio("Sector View Metric:", ["Total Amount ($ Millions)", "Deal Count"], horizontal=True)

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Top Sectors Distribution")
        if sector_metric_option == "Total Amount ($ Millions)":
            raw_sector = df.groupby('industry')['amount'].sum()
        else:
            raw_sector = df.groupby('industry')['amount'].count()
        
        sector_series = get_top_n_series(raw_sector, n=5)
        fig1, ax1 = plt.subplots(figsize=(5, 4))
        ax1.pie(sector_series, labels=sector_series.index, autopct='%1.1f%%', colors=sns.color_palette("Blues_r", len(sector_series)), startangle=140)
        ax1.set_title(f"Top Sectors by {sector_metric_option}", fontsize=11, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig1)

    with col_b:
        st.subheader("Top 10 Cities by Funding")
        top_cities = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10).reset_index()
        top_cities['amount_m'] = top_cities['amount'] / 1e6
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.barplot(data=top_cities, x='amount_m', y='city', palette='Greens_r', ax=ax2)
        ax2.set_xlabel("Total Amount ($ Millions)")
        ax2.set_ylabel("City")
        ax2.ticklabel_format(style='plain', axis='x', useOffset=False)
        plt.tight_layout()
        st.pyplot(fig2)

    st.write("---")

    # Investment Type & Heatmap
    col_c, col_d = st.columns(2)
    
    with col_c:
        st.subheader("Funding Stage Distribution (Top 5)")
        stage_raw = df.groupby('investment_type')['amount'].sum()
        stage_series = get_top_n_series(stage_raw, n=5)
        fig3, ax3 = plt.subplots(figsize=(5, 4))
        ax3.pie(stage_series, labels=stage_series.index, autopct='%1.1f%%', colors=sns.color_palette("pastel", len(stage_series)), startangle=140)
        plt.tight_layout()
        st.pyplot(fig3)

    with col_d:
        st.subheader("Yearly Funding Heatmap ($ Millions)")
        pivot_df = df.pivot_table(index='month', columns='year', values='amount', aggfunc='sum').fillna(0) / 1e6
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        sns.heatmap(pivot_df, cmap='YlGnBu', ax=ax4, cbar_kws={'label': '$ Millions'}, fmt='.0f')
        ax4.set_xlabel("Year")
        ax4.set_ylabel("Month")
        plt.tight_layout()
        st.pyplot(fig4)

    st.write("---")

    # Top Startups (Year-wise & Overall Leaderboard)
    st.header("Top Funded Startups Leaderboard")
    years_list = ["All Years"] + sorted([int(y) for y in df['year'].dropna().unique()], reverse=True)
    selected_year = st.selectbox("Filter by Year:", years_list)

    if selected_year == "All Years":
        filtered_df = df
    else:
        filtered_df = df[df['year'] == selected_year]

    top_startups_df = filtered_df.groupby(['startup', 'industry', 'city']).agg(
        Total_Funding=('amount', 'sum'),
        Total_Rounds=('amount', 'count')
    ).reset_index().sort_values('Total_Funding', ascending=False).head(15)

    top_startups_df['Total Funding'] = top_startups_df['Total_Funding'].apply(format_currency)
    st.dataframe(
        top_startups_df[['startup', 'industry', 'city', 'Total Funding', 'Total_Rounds']].rename(
            columns={'startup': 'Startup', 'industry': 'Industry', 'city': 'City', 'Total_Rounds': 'Rounds'}
        ),
        use_container_width=True,
        hide_index=True
    )

    # Top Active Investors Leaderboard
    st.subheader("Top 10 Active Investors")
    all_inv_list = []
    for invs in df['investors'].dropna():
        for i in str(invs).split(','):
            clean_i = i.strip()
            if clean_i and clean_i.lower() not in ['undisclosed investors', 'undisclosed']:
                all_inv_list.append(clean_i)
    
    top_inv_series = pd.Series(all_inv_list).value_counts().head(10).reset_index()
    top_inv_series.columns = ['Investor', 'Deals Count']
    
    fig_inv, ax_inv = plt.subplots(figsize=(8, 3.5))
    sns.barplot(data=top_inv_series, x='Deals Count', y='Investor', palette='rocket', ax=ax_inv)
    ax_inv.set_xlabel("Number of Investments")
    plt.tight_layout()
    st.pyplot(fig_inv)

# 2. STARTUP ANALYSIS
# ---------------------------------------------------------
def load_startup_details(startup_name):
    st.title(startup_name)
    
    startup_df = df[df['startup'] == startup_name].sort_values('Date', ascending=False).copy()
    if startup_df.empty:
        st.warning("No details found for this startup.")
        return

    total_raised = startup_df['amount'].sum()
    rounds_count = len(startup_df)
    industry = startup_df['industry'].iloc[0]
    city = startup_df['city'].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Raised", format_currency(total_raised))
    with col2:
        st.metric("Rounds Count", rounds_count)
    with col3:
        st.metric("Industry", industry)
    with col4:
        st.metric("City", city)

    st.write("---")

    st.subheader("Funding Rounds History")
    display_df = startup_df[['Date', 'investment_type', 'investors', 'amount', 'city']].copy()
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df['amount'] = display_df['amount'].apply(format_currency)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("Funding Progression")
        startup_df['amount_m'] = startup_df['amount'] / 1e6
        fig_s1, ax_s1 = plt.subplots(figsize=(6, 4))
        sns.barplot(data=startup_df, x='Date', y='amount_m', ax=ax_s1, palette='Blues_r')
        ax_s1.set_xlabel("Date")
        ax_s1.set_ylabel("Amount ($ Millions)")
        ax_s1.ticklabel_format(style='plain', axis='y', useOffset=False)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig_s1)

    with col_s2:
        st.subheader("Investment Type Breakdown")
        raw_stage = startup_df.groupby('investment_type')['amount'].sum()
        stage_counts = get_top_n_series(raw_stage, n=5)
        fig_s2, ax_s2 = plt.subplots(figsize=(5, 4))
        ax_s2.pie(stage_counts, labels=stage_counts.index, autopct='%1.1f%%', colors=sns.color_palette("Set2", len(stage_counts)), startangle=140)
        plt.tight_layout()
        st.pyplot(fig_s2)

    st.write("---")

    # Similar Companies Section
    st.subheader("🔍 Similar Companies in " + industry)
    similar_df = df[(df['industry'] == industry) & (df['startup'] != startup_name)]
    if not similar_df.empty:
        similar_summary = similar_df.groupby('startup').agg(
            Total_Funding=('amount', 'sum'),
            City=('city', 'first'),
            Sub_Vertical=('sub_vertical', 'first')
        ).reset_index().sort_values('Total_Funding', ascending=False).head(5)
        
        similar_summary['Total Funding'] = similar_summary['Total_Funding'].apply(format_currency)
        st.dataframe(
            similar_summary[['startup', 'Sub_Vertical', 'City', 'Total Funding']].rename(
                columns={'startup': 'Startup', 'Sub_Vertical': 'Sub Industry'}
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No similar companies found in this industry.")

# 3. INVESTOR ANALYSIS
# ---------------------------------------------------------
def load_investor_details(investor_name):
    st.title(investor_name)

    investor_mask = df['investors'].fillna('').str.contains(investor_name, regex=False)
    investor_df = df[investor_mask].sort_values('Date', ascending=False).copy()
    
    if investor_df.empty:
        st.warning("No investment details found for this investor.")
        return

    total_invested = investor_df['amount'].sum()
    startups_backed = investor_df['startup'].nunique()
    deals_count = len(investor_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Capital Invested", format_currency(total_invested))
    with col2:
        st.metric("Startups Backed", startups_backed)
    with col3:
        st.metric("Total Deals", deals_count)

    st.write("---")

    st.subheader("Most Recent Investments")
    recent_df = investor_df[['Date', 'startup', 'industry', 'city', 'investment_type', 'amount']].copy()
    recent_df['Date'] = recent_df['Date'].dt.strftime('%Y-%m-%d')
    recent_df['amount'] = recent_df['amount'].apply(format_currency)
    st.dataframe(recent_df, use_container_width=True, hide_index=True)

    st.write("---")

    # Investor Pie Charts (Sector, Stage, City)
    col_i1, col_i2, col_i3 = st.columns(3)
    
    with col_i1:
        st.subheader("Sector -> Pie")
        raw_sector = investor_df.groupby('industry')['amount'].sum()
        sector_series = get_top_n_series(raw_sector, n=5)
        fig_i1, ax_i1 = plt.subplots(figsize=(4.5, 4))
        ax_i1.pie(sector_series, labels=sector_series.index, autopct='%1.1f%%', colors=sns.color_palette("Spectral", len(sector_series)), startangle=140)
        plt.tight_layout()
        st.pyplot(fig_i1)

    with col_i2:
        st.subheader("Stage -> Pie")
        raw_stage = investor_df.groupby('investment_type')['amount'].sum()
        stage_series = get_top_n_series(raw_stage, n=5)
        fig_i2, ax_i2 = plt.subplots(figsize=(4.5, 4))
        ax_i2.pie(stage_series, labels=stage_series.index, autopct='%1.1f%%', colors=sns.color_palette("Pastel1", len(stage_series)), startangle=140)
        plt.tight_layout()
        st.pyplot(fig_i2)

    with col_i3:
        st.subheader("City -> Pie")
        raw_city = investor_df.groupby('city')['amount'].sum()
        city_series = get_top_n_series(raw_city, n=5)
        fig_i3, ax_i3 = plt.subplots(figsize=(4.5, 4))
        ax_i3.pie(city_series, labels=city_series.index, autopct='%1.1f%%', colors=sns.color_palette("Set3", len(city_series)), startangle=140)
        plt.tight_layout()
        st.pyplot(fig_i3)

    st.write("---")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.subheader("Biggest Investments")
        big_series = investor_df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(5).reset_index()
        big_series['amount_m'] = big_series['amount'] / 1e6
        fig_big, ax_big = plt.subplots(figsize=(6, 4))
        sns.barplot(data=big_series, x='amount_m', y='startup', palette='viridis', ax=ax_big)
        ax_big.set_xlabel("Capital Invested ($ Millions)")
        ax_big.set_ylabel("Startup")
        ax_big.ticklabel_format(style='plain', axis='x', useOffset=False)
        plt.tight_layout()
        st.pyplot(fig_big)

    with col_b2:
        st.subheader("YoY Investment Activity")
        year_series = investor_df.groupby('year')['amount'].sum().reset_index()
        year_series['amount_m'] = year_series['amount'] / 1e6
        fig_yoy, ax_yoy = plt.subplots(figsize=(6, 4))
        sns.barplot(data=year_series, x='year', y='amount_m', palette='mako', ax=ax_yoy)
        ax_yoy.set_xlabel("Year")
        ax_yoy.set_ylabel("Total Amount ($ Millions)")
        ax_yoy.ticklabel_format(style='plain', axis='y', useOffset=False)
        plt.tight_layout()
        st.pyplot(fig_yoy)

    st.write("---")

    # Similar Investors Section
    st.subheader("🤝 Similar Investors")
    top_inv_sectors = investor_df.groupby('industry')['amount'].sum().sort_values(ascending=False).head(3).index.tolist()
    if top_inv_sectors:
        sector_match_mask = df['industry'].isin(top_inv_sectors)
        matched_df = df[sector_match_mask]
        
        sim_inv_list = []
        for invs in matched_df['investors'].dropna():
            for i in str(invs).split(','):
                clean_i = i.strip()
                if clean_i and clean_i.lower() not in ['undisclosed investors', 'undisclosed'] and clean_i != investor_name:
                    sim_inv_list.append(clean_i)
        
        if sim_inv_list:
            sim_inv_series = pd.Series(sim_inv_list).value_counts().head(5).reset_index()
            sim_inv_series.columns = ['Investor Name', 'Co-Investments / Shared Sector Deals']
            st.dataframe(sim_inv_series, use_container_width=True, hide_index=True)
        else:
            st.info("No similar investors found.")

# Router
# ---------------------------------------------------------
if option == "Overall Analysis":
    load_overall_analysis()

elif option == "StartUp":
    selected_startup = st.sidebar.selectbox("Select StartUp", sorted(df['startup'].dropna().unique().tolist()))
    btn1 = st.sidebar.button("Find StartUp Details")
    if btn1:
        load_startup_details(selected_startup)
    else:
        load_startup_details(selected_startup)

else:
    investors_list = extract_investors()
    selected_investor = st.sidebar.selectbox("Select Investor", investors_list)
    btn2 = st.sidebar.button("Find Investor Details")
    if btn2:
        load_investor_details(selected_investor)
    else:
        load_investor_details(selected_investor)
