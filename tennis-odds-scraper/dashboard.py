"""
Tennis Odds Dashboard with Multiple Data Sources
Streamlit dashboard with Demo, Production Scraping, and Live API modes
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.demo_scraper import DemoScraper
from scrapers.oddsportal_scraper import OddsPortalScraper
from scrapers.theodds_scraper import TheOddsAPIScraper
from exporters.csv_exporter import CSVExporter
from exporters.excel_exporter import ExcelExporter

# Page configuration
st.set_page_config(
    page_title="Tennis Odds Tracker",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .data-mode-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.875rem;
    }
    .mode-demo { background-color: #90EE90; color: #000; }
    .mode-production { background-color: #FFB6C1; color: #000; }
    .mode-api { background-color: #87CEEB; color: #000; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'matches_df' not in st.session_state:
    st.session_state.matches_df = None
if 'last_scrape_time' not in st.session_state:
    st.session_state.last_scrape_time = None
if 'data_mode' not in st.session_state:
    st.session_state.data_mode = 'Demo Mode'
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('ODDS_API_KEY', '')


def get_mode_badge(mode: str) -> str:
    """Generate HTML badge for data mode"""
    mode_classes = {
        'Demo Mode': 'mode-demo',
        'Production Mode': 'mode-production',
        'API Mode (Live)': 'mode-api'
    }
    return f'<span class="data-mode-badge {mode_classes.get(mode, "")}">{mode}</span>'


def scrape_data(mode: str, api_key: str = None) -> pd.DataFrame:
    """
    Scrape tennis matches based on selected mode
    
    Args:
        mode: Data source mode
        api_key: The Odds API key (required for API mode)
        
    Returns:
        DataFrame with matches
    """
    with st.spinner(f'Fetching data from {mode}...'):
        try:
            if mode == 'Demo Mode':
                # Demo mode - simulated data
                with DemoScraper() as scraper:
                    matches = scraper.scrape_tennis_matches()
                    st.success(f"✅ Loaded {len(matches)} demo matches")
            
            elif mode == 'Production Mode':
                # Production scraping from Oddsportal
                with OddsPortalScraper() as scraper:
                    matches = scraper.scrape_tennis_matches()
                    st.success(f"✅ Scraped {len(matches)} matches from Oddsportal")
            
            elif mode == 'API Mode (Live)':
                # Live API mode
                if not api_key:
                    st.error("❌ API key required for API Mode")
                    st.info("👉 Get your free API key at: https://the-odds-api.com/")
                    st.stop()
                
                with TheOddsAPIScraper(api_key) as scraper:
                    matches = scraper.scrape_tennis_matches(
                        include_atp=True,
                        include_wta=True
                    )
                    
                    # Show API status
                    status = scraper.get_api_status()
                    if status['requests_remaining']:
                        st.info(f"📊 API Requests Remaining: {status['requests_remaining']}/{status['free_tier_limit']}")
                    
                    if matches:
                        st.success(f"✅ Fetched {len(matches)} live matches from The Odds API")
                    else:
                        st.warning("⚠️ No live matches found (may be off-season or no tournaments active)")
            
            # Convert to DataFrame
            if matches:
                df = pd.DataFrame(matches)
                st.session_state.last_scrape_time = datetime.now()
                return df
            else:
                st.warning("No matches found")
                return pd.DataFrame()
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return pd.DataFrame()


def display_metrics(df: pd.DataFrame):
    """Display key metrics"""
    if df.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Matches", len(df))
    
    with col2:
        avg_margin = df['bookmaker_margin'].mean()
        st.metric("Avg Margin", f"{avg_margin:.2f}%")
    
    with col3:
        best_value = df.nsmallest(1, 'bookmaker_margin')
        if not best_value.empty:
            st.metric("Best Value", f"{best_value.iloc[0]['bookmaker_margin']:.2f}%")
    
    with col4:
        unique_tournaments = df['tournament'].nunique()
        st.metric("Tournaments", unique_tournaments)


def plot_margin_distribution(df: pd.DataFrame):
    """Plot bookmaker margin distribution"""
    fig = px.histogram(
        df,
        x='bookmaker_margin',
        nbins=20,
        title='Bookmaker Margin Distribution',
        labels={'bookmaker_margin': 'Margin (%)', 'count': 'Frequency'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_layout(
        xaxis_title="Margin (%)",
        yaxis_title="Number of Matches",
        showlegend=False,
        height=400
    )
    
    return fig


def plot_odds_comparison(df: pd.DataFrame):
    """Plot odds comparison scatter"""
    fig = px.scatter(
        df,
        x='odds_player1',
        y='odds_player2',
        color='bookmaker_margin',
        hover_data=['player1', 'player2', 'tournament'],
        title='Odds Comparison (Player 1 vs Player 2)',
        labels={
            'odds_player1': 'Player 1 Odds',
            'odds_player2': 'Player 2 Odds',
            'bookmaker_margin': 'Margin (%)'
        },
        color_continuous_scale='RdYlGn_r'
    )
    
    fig.update_layout(height=400)
    
    return fig


def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎾 Tennis Odds Tracker</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Data mode selection
        st.subheader("📊 Data Source")
        
        data_mode = st.radio(
            "Select data source:",
            [
                "Demo Mode",
                "Production Mode",
                "API Mode (Live)"
            ],
            index=0,
            help="""
            **Demo Mode**: Simulated realistic data (instant, always works)
            **Production Mode**: Web scraping from Oddsportal (requires internet)
            **API Mode**: Real-time data from The Odds API (requires API key)
            """
        )
        
        st.session_state.data_mode = data_mode
        
        # Mode info
        if data_mode == "Demo Mode":
            st.info("💡 **Demo Mode**\n\nSimulated data for presentations and testing. Always available, no external dependencies.")
        
        elif data_mode == "Production Mode":
            st.warning("⚠️ **Production Mode**\n\nReal web scraping. May require updates if site structure changes.")
        
        elif data_mode == "API Mode (Live)":
            st.success("✨ **API Mode**\n\nReal-time data from 200+ bookmakers via The Odds API.")
            
            # API key input
            api_key_input = st.text_input(
                "The Odds API Key",
                value=st.session_state.api_key,
                type="password",
                help="Get your free API key at https://the-odds-api.com/"
            )
            
            st.session_state.api_key = api_key_input
            
            if not api_key_input:
                st.info("👉 [Get Free API Key](https://the-odds-api.com/)")
        
        st.markdown("---")
        
        # Scrape button
        if st.button("🔄 Scrape Now", type="primary", use_container_width=True):
            df = scrape_data(data_mode, st.session_state.api_key)
            if not df.empty:
                st.session_state.matches_df = df
        
        # Last update info
        if st.session_state.last_scrape_time:
            st.caption(f"Last update: {st.session_state.last_scrape_time.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Filters (if data loaded)
        if st.session_state.matches_df is not None and not st.session_state.matches_df.empty:
            st.subheader("🔍 Filters")
            
            df = st.session_state.matches_df
            
            # Tournament filter
            tournaments = ['All'] + sorted(df['tournament'].unique().tolist())
            selected_tournament = st.selectbox("Tournament", tournaments)
            
            # Margin filter
            max_margin = st.slider(
                "Max Margin (%)",
                min_value=0.0,
                max_value=float(df['bookmaker_margin'].max()),
                value=float(df['bookmaker_margin'].max()),
                step=0.5
            )
            
            # Apply filters
            filtered_df = df.copy()
            
            if selected_tournament != 'All':
                filtered_df = filtered_df[filtered_df['tournament'] == selected_tournament]
            
            filtered_df = filtered_df[filtered_df['bookmaker_margin'] <= max_margin]
            
            st.session_state.matches_df = filtered_df
            
            st.caption(f"Showing {len(filtered_df)} matches")
    
    # Main content
    if st.session_state.matches_df is None or st.session_state.matches_df.empty:
        st.info("👈 Select a data source and click 'Scrape Now' to load matches")
        
        # Show data mode descriptions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎮 Demo Mode")
            st.markdown("""
            - ✅ Instant loading
            - ✅ Always available
            - ✅ Realistic data
            - ✅ Perfect for presentations
            """)
        
        with col2:
            st.markdown("### 🌐 Production Mode")
            st.markdown("""
            - ✅ Real scraping
            - ✅ Oddsportal data
            - ⚠️ May need updates
            - ✅ Shows technical skills
            """)
        
        with col3:
            st.markdown("### ⚡ API Mode")
            st.markdown("""
            - ✅ Real-time data
            - ✅ 200+ bookmakers
            - ✅ ATP & WTA
            - ✅ 500 free req/month
            """)
        
        return
    
    df = st.session_state.matches_df
    
    # Display mode badge
    st.markdown(f"**Current Mode:** {get_mode_badge(st.session_state.data_mode)}", unsafe_allow_html=True)
    st.markdown("---")
    
    # Metrics
    display_metrics(df)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "🎯 Best Value", "💾 Export"])
    
    # Tab 1: Overview
    with tab1:
        st.header("All Matches")
        
        # Display matches
        for idx, match in df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{match['player1']}** vs **{match['player2']}**")
                    st.caption(f"🏆 {match['tournament']} | 📅 {match['match_time']}")
                
                with col2:
                    st.metric("Player 1", f"{match['odds_player1']:.2f}")
                
                with col3:
                    st.metric("Player 2", f"{match['odds_player2']:.2f}")
                
                with col4:
                    st.metric("Margin", f"{match['bookmaker_margin']:.2f}%")
                
                st.caption(f"💰 {match['bookmaker']}")
                st.markdown("---")
    
    # Tab 2: Analytics
    with tab2:
        st.header("📈 Analytics Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(plot_margin_distribution(df), use_container_width=True)
        
        with col2:
            st.plotly_chart(plot_odds_comparison(df), use_container_width=True)
        
        # Tournament breakdown
        st.subheader("Tournament Breakdown")
        tournament_stats = df.groupby('tournament').agg({
            'bookmaker_margin': ['mean', 'min', 'count']
        }).round(2)
        
        st.dataframe(tournament_stats, use_container_width=True)
    
    # Tab 3: Best Value
    with tab3:
        st.header("🎯 Best Value Bets")
        st.caption("Matches with lowest bookmaker margins (better value for bettors)")
        
        best_value = df.nsmallest(10, 'bookmaker_margin')
        
        for idx, match in best_value.iterrows():
            with st.expander(f"✨ {match['player1']} vs {match['player2']} - {match['bookmaker_margin']:.2f}% margin"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Match Details:**
                    - Tournament: {match['tournament']}
                    - Time: {match['match_time']}
                    - Bookmaker: {match['bookmaker']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Odds:**
                    - {match['player1']}: **{match['odds_player1']:.2f}**
                    - {match['player2']}: **{match['odds_player2']:.2f}**
                    - Margin: **{match['bookmaker_margin']:.2f}%**
                    """)
    
    # Tab 4: Export
    with tab4:
        st.header("💾 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("CSV Export")
            
            csv_exporter = CSVExporter()
            csv_data = df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"tennis_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.subheader("Excel Export")
            st.info("Excel export with formatting available via CLI: `python main.py --format excel`")
        
        st.markdown("---")
        st.caption(f"Dataset: {len(df)} matches | Mode: {st.session_state.data_mode}")


if __name__ == "__main__":
    main()
