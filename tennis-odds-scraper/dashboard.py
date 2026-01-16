"""
Streamlit Dashboard for Tennis Odds Analysis
Interactive web interface for real-time odds visualization and analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from scrapers import OddsportalScraper
from exporters import CSVExporter, ExcelExporter
from utils import calculate_implied_probability, calculate_bookmaker_margin

# Page configuration
st.set_page_config(
    page_title="Tennis Odds Dashboard",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def scrape_odds(bookmaker):
    """Scrape odds with caching"""
    if bookmaker == "Oddsportal":
        with OddsportalScraper() as scraper:
            matches = scraper.scrape_tennis_matches()
        return matches
    return []


def calculate_metrics(df):
    """Calculate key metrics from dataframe"""
    if df.empty:
        return {
            'total_matches': 0,
            'avg_margin': 0.0,
            'tournaments': 0,
            'best_value_margin': 0.0
        }
    
    return {
        'total_matches': len(df),
        'avg_margin': df['bookmaker_margin'].mean() if 'bookmaker_margin' in df else 0.0,
        'tournaments': df['tournament'].nunique() if 'tournament' in df else 0,
        'best_value_margin': df['bookmaker_margin'].min() if 'bookmaker_margin' in df else 0.0
    }


def create_odds_distribution_chart(df):
    """Create odds distribution histogram"""
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['odds_player1'],
        name='Player 1 Odds',
        marker_color='#1f77b4',
        opacity=0.7
    ))
    
    fig.add_trace(go.Histogram(
        x=df['odds_player2'],
        name='Player 2 Odds',
        marker_color='#ff7f0e',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Odds Distribution',
        xaxis_title='Odds (Decimal)',
        yaxis_title='Frequency',
        barmode='overlay',
        height=400
    )
    
    return fig


def create_margin_by_tournament_chart(df):
    """Create margin by tournament bar chart"""
    if df.empty or 'tournament' not in df:
        return go.Figure()
    
    avg_margins = df.groupby('tournament')['bookmaker_margin'].mean().sort_values()
    
    fig = go.Figure(data=[
        go.Bar(
            x=avg_margins.values,
            y=avg_margins.index,
            orientation='h',
            marker_color='#2ca02c'
        )
    ])
    
    fig.update_layout(
        title='Average Bookmaker Margin by Tournament',
        xaxis_title='Average Margin (%)',
        yaxis_title='Tournament',
        height=400
    )
    
    return fig


def create_implied_probability_chart(df):
    """Create scatter plot of implied probabilities"""
    if df.empty:
        return go.Figure()
    
    fig = px.scatter(
        df,
        x='implied_prob1',
        y='implied_prob2',
        color='bookmaker_margin',
        size='bookmaker_margin',
        hover_data=['player1', 'player2', 'tournament'],
        title='Implied Probabilities Analysis',
        labels={
            'implied_prob1': 'Player 1 Implied Probability (%)',
            'implied_prob2': 'Player 2 Implied Probability (%)',
            'bookmaker_margin': 'Margin (%)'
        },
        color_continuous_scale='RdYlGn_r'
    )
    
    fig.update_layout(height=500)
    
    return fig


def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🎾 Tennis Odds Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Bookmaker selection
        bookmaker = st.selectbox(
            "Select Bookmaker",
            ["Oddsportal"],
            help="Choose which bookmaker to scrape odds from"
        )
        
        st.divider()
        
        # Scraping controls
        st.subheader("🔄 Data Collection")
        
        auto_refresh = st.checkbox(
            "Auto-refresh (30s)",
            help="Automatically refresh data every 30 seconds"
        )
        
        scrape_button = st.button("🚀 Scrape Now", type="primary")
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        
        margin_threshold = st.slider(
            "Max Margin (%)",
            min_value=0.0,
            max_value=10.0,
            value=10.0,
            step=0.5,
            help="Filter matches by maximum bookmaker margin"
        )
        
        min_odds = st.slider(
            "Min Odds",
            min_value=1.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Minimum odds to display"
        )
        
        st.divider()
        
        # Export section
        st.subheader("💾 Export Data")
        export_format = st.selectbox("Format", ["CSV", "Excel"])
        export_button = st.button("📥 Export")
    
    # Main content
    if scrape_button or auto_refresh:
        with st.spinner(f"🔍 Scraping odds from {bookmaker}..."):
            matches = scrape_odds(bookmaker)
            
            if not matches:
                st.error("❌ No matches found. The website structure may have changed.")
                st.stop()
            
            # Convert to DataFrame
            df = pd.DataFrame(matches)
            
            # Add calculated fields
            df['implied_prob1'] = df['odds_player1'].apply(
                lambda x: calculate_implied_probability(x)
            )
            df['implied_prob2'] = df['odds_player2'].apply(
                lambda x: calculate_implied_probability(x)
            )
            df['bookmaker_margin'] = df.apply(
                lambda row: calculate_bookmaker_margin(
                    row['odds_player1'],
                    row['odds_player2']
                ),
                axis=1
            )
            
            # Store in session state
            st.session_state['df'] = df
            st.session_state['last_update'] = datetime.now()
        
        st.success(f"✅ Successfully scraped {len(matches)} matches!")
    
    # Check if data exists
    if 'df' not in st.session_state:
        st.info("👆 Click 'Scrape Now' to fetch the latest tennis odds data")
        st.stop()
    
    df = st.session_state['df'].copy()
    
    # Apply filters
    df = df[df['bookmaker_margin'] <= margin_threshold]
    df = df[(df['odds_player1'] >= min_odds) | (df['odds_player2'] >= min_odds)]
    
    # Display last update time
    if 'last_update' in st.session_state:
        st.caption(f"🕒 Last updated: {st.session_state['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Metrics
    st.header("📊 Key Metrics")
    metrics = calculate_metrics(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Matches",
            value=metrics['total_matches'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Average Margin",
            value=f"{metrics['avg_margin']:.2f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Tournaments",
            value=metrics['tournaments'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Best Value",
            value=f"{metrics['best_value_margin']:.2f}%",
            delta=None,
            help="Lowest margin found (best value for bettors)"
        )
    
    st.divider()
    
    # Charts
    st.header("📈 Visual Analysis")
    
    tab1, tab2, tab3 = st.tabs(["📊 Odds Distribution", "🏆 By Tournament", "🎯 Probability Analysis"])
    
    with tab1:
        fig1 = create_odds_distribution_chart(df)
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("""
        **Interpretation:**
        - Lower odds = Higher probability (favorites)
        - Higher odds = Lower probability (underdogs)
        - Distribution shows market's assessment of match outcomes
        """)
    
    with tab2:
        fig2 = create_margin_by_tournament_chart(df)
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        **Interpretation:**
        - Lower margins = Better value for bettors
        - Margins vary by tournament prestige and liquidity
        - Major tournaments typically have lower margins
        """)
    
    with tab3:
        fig3 = create_implied_probability_chart(df)
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("""
        **Interpretation:**
        - Points closer to diagonal = More balanced matches
        - Color indicates bookmaker margin (green = lower, red = higher)
        - Hover for match details
        """)
    
    st.divider()
    
    # Best Value Bets
    st.header("💎 Best Value Bets")
    st.caption("Matches with the lowest bookmaker margins (best opportunities)")
    
    best_value = df.nsmallest(10, 'bookmaker_margin')
    
    if not best_value.empty:
        # Format dataframe for display
        display_df = best_value[[
            'tournament', 'player1', 'player2',
            'odds_player1', 'odds_player2', 'bookmaker_margin'
        ]].copy()
        
        display_df['bookmaker_margin'] = display_df['bookmaker_margin'].apply(
            lambda x: f"{x:.2f}%"
        )
        
        display_df.columns = [
            'Tournament', 'Player 1', 'Player 2',
            'Odds 1', 'Odds 2', 'Margin'
        ]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No matches found with current filters")
    
    st.divider()
    
    # All Matches Table
    st.header("📋 All Matches")
    
    # Search functionality
    search_term = st.text_input("🔍 Search by player or tournament", "")
    
    filtered_df = df.copy()
    if search_term:
        mask = (
            filtered_df['player1'].str.contains(search_term, case=False, na=False) |
            filtered_df['player2'].str.contains(search_term, case=False, na=False) |
            filtered_df['tournament'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Display table
    if not filtered_df.empty:
        display_cols = [
            'timestamp', 'tournament', 'player1', 'player2',
            'odds_player1', 'odds_player2', 'bookmaker_margin',
            'match_date', 'match_time'
        ]
        
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        
        st.dataframe(
            filtered_df[available_cols],
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Showing {len(filtered_df)} matches")
    else:
        st.info("No matches found with current search and filters")
    
    # Export functionality
    if export_button and 'df' in st.session_state:
        df_export = st.session_state['df']
        
        with st.spinner("Exporting data..."):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if export_format == "CSV":
                exporter = CSVExporter()
                filename = f"tennis_odds_{timestamp}.csv"
                filepath = exporter.export(df_export.to_dict('records'), filename)
                
            else:  # Excel
                exporter = ExcelExporter()
                filename = f"tennis_odds_{timestamp}.xlsx"
                filepath = exporter.export(
                    df_export.to_dict('records'),
                    filename,
                    include_summary=True
                )
            
            st.sidebar.success(f"✅ Exported to: {filepath}")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()
