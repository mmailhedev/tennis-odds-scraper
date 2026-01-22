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

# Import scrapers
from scrapers.demo_scraper import DemoScraper
from scrapers.oddsportal_scraper import OddsportalScraper
from scrapers.theodds_scraper import TheOddsAPIScraper

# Import exporters
from exporters.csv_exporter import CSVExporter

# Try to import Excel exporter
try:
    from exporters.excel_exporter import ExcelExporter
    EXCEL_EXPORT_AVAILABLE = True
except ImportError:
    EXCEL_EXPORT_AVAILABLE = False

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
if 'raw_matches_df' not in st.session_state:
    st.session_state.raw_matches_df = None
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


def calculate_bookmaker_margin(odds1: float, odds2: float) -> float:
    """Calculate bookmaker margin from odds"""
    if odds1 <= 0 or odds2 <= 0:
        return 0.0
    
    implied_prob_sum = (1 / odds1) + (1 / odds2)
    margin = (implied_prob_sum - 1) * 100
    
    return round(margin, 2)


def scrape_data(mode: str, api_key: str = None) -> pd.DataFrame:
    """Scrape tennis matches based on selected mode"""
    with st.spinner(f'Fetching data from {mode}...'):
        try:
            matches = []
            
            if mode == 'Demo Mode':
                with DemoScraper() as scraper:
                    matches = scraper.scrape_tennis_matches()
                    st.success(f"✅ Loaded {len(matches)} demo matches")
            
            elif mode == 'Production Mode':
                with OddsportalScraper() as scraper:
                    matches = scraper.scrape_tennis_matches()
                    st.success(f"✅ Scraped {len(matches)} matches from Oddsportal")
            
            elif mode == 'API Mode (Live)':
                if not api_key:
                    st.error("❌ API key required for API Mode")
                    st.info("👉 Get your free API key at: https://the-odds-api.com/")
                    st.stop()
                
                with TheOddsAPIScraper(api_key) as scraper:
                    matches = scraper.scrape_tennis_matches(
                        include_atp=True,
                        include_wta=True
                    )
                    
                    status = scraper.get_api_status()
                    if status['requests_remaining']:
                        st.info(f"📊 API Requests Remaining: {status['requests_remaining']}/{status['free_tier_limit']}")
                    
                    if matches:
                        st.success(f"✅ Fetched {len(matches)} live matches")
                    else:
                        st.warning("⚠️ No live matches found")
            
            if matches:
                df = pd.DataFrame(matches)
                
                # Ensure bookmaker_margin exists
                if 'bookmaker_margin' not in df.columns:
                    df['bookmaker_margin'] = df.apply(
                        lambda row: calculate_bookmaker_margin(row['odds_player1'], row['odds_player2']), 
                        axis=1
                    )
                
                st.session_state.last_scrape_time = datetime.now()
                return df
            else:
                return pd.DataFrame()
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return pd.DataFrame()


def apply_filters(df: pd.DataFrame, tournament_filter: str, margin_filter: float) -> pd.DataFrame:
    """Apply filters to dataframe without modifying session state"""
    filtered = df.copy()
    
    if tournament_filter != 'All':
        filtered = filtered[filtered['tournament'] == tournament_filter]
    
    filtered = filtered[filtered['bookmaker_margin'] <= margin_filter]
    
    return filtered


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
            ["Demo Mode", "Production Mode", "API Mode (Live)"],
            index=0
        )
        
        st.session_state.data_mode = data_mode
        
        # Mode info
        if data_mode == "Demo Mode":
            st.info("💡 Demo data - instant, always works")
        elif data_mode == "Production Mode":
            st.warning("⚠️ Real scraping - may need updates")
        elif data_mode == "API Mode (Live)":
            st.success("✨ Real-time API data")
            
            api_key_input = st.text_input(
                "The Odds API Key",
                value=st.session_state.api_key,
                type="password"
            )
            
            st.session_state.api_key = api_key_input
            
            if not api_key_input:
                st.info("👉 [Get Free API Key](https://the-odds-api.com/)")
        
        st.markdown("---")
        
        # Scrape button
        if st.button("🔄 Scrape Now", type="primary", use_container_width=True):
            df = scrape_data(data_mode, st.session_state.api_key)
            if not df.empty:
                st.session_state.raw_matches_df = df  # Store RAW data, don't filter here
        
        # Last update
        if st.session_state.last_scrape_time:
            st.caption(f"Last update: {st.session_state.last_scrape_time.strftime('%H:%M:%S')}")
    
    # Main content
    if st.session_state.raw_matches_df is None or st.session_state.raw_matches_df.empty:
        st.info("👈 Select a data source and click 'Scrape Now'")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎮 Demo Mode")
            st.markdown("- ✅ Instant\n- ✅ Reliable\n- ✅ Realistic data")
        
        with col2:
            st.markdown("### 🌐 Production Mode")
            st.markdown("- ✅ Real scraping\n- ✅ Oddsportal\n- ⚠️ Requires updates")
        
        with col3:
            st.markdown("### ⚡ API Mode")
            st.markdown("- ✅ Real-time\n- ✅ 200+ bookmakers\n- ✅ Free tier")
        
        return
    
    # Apply filters WITHOUT modifying session state
    raw_df = st.session_state.raw_matches_df
    
    # Filters in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔍 Filters")
        
        tournaments = ['All'] + sorted(raw_df['tournament'].unique().tolist())
        selected_tournament = st.selectbox("Tournament", tournaments)
        
        max_margin = st.slider(
            "Max Margin (%)",
            min_value=0.0,
            max_value=float(raw_df['bookmaker_margin'].max()),
            value=float(raw_df['bookmaker_margin'].max()),
            step=0.5
        )
    
    # Apply filters to get display dataframe
    display_df = apply_filters(raw_df, selected_tournament, max_margin)
    
    # Show results count
    st.caption(f"Showing {len(display_df)} of {len(raw_df)} matches")
    
    # Display mode badge
    st.markdown(f"**Mode:** {get_mode_badge(st.session_state.data_mode)}", unsafe_allow_html=True)
    st.markdown("---")
    
    # Metrics
    display_metrics(display_df)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "🎯 Best Value", "💾 Export"])
    
    with tab1:
        st.header("All Matches")
        
        for idx, match in display_df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{match['player1']}** vs **{match['player2']}**")
                st.caption(f"🏆 {match['tournament']}")
            
            with col2:
                st.metric("Player 1", f"{match['odds_player1']:.2f}")
            
            with col3:
                st.metric("Player 2", f"{match['odds_player2']:.2f}")
            
            with col4:
                st.metric("Margin", f"{match['bookmaker_margin']:.2f}%")
            
            st.markdown("---")
    
    with tab2:
        st.header("📈 Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(plot_margin_distribution(display_df), use_container_width=True)
        
        with col2:
            st.plotly_chart(plot_odds_comparison(display_df), use_container_width=True)
    
    with tab3:
        st.header("🎯 Best Value Bets")
        
        best_value = display_df.nsmallest(10, 'bookmaker_margin')
        
        for idx, match in best_value.iterrows():
            with st.expander(f"✨ {match['player1']} vs {match['player2']} - {match['bookmaker_margin']:.2f}%"):
                st.markdown(f"""
                **Tournament:** {match['tournament']}  
                **Odds:** {match['odds_player1']:.2f} / {match['odds_player2']:.2f}  
                **Margin:** {match['bookmaker_margin']:.2f}%
                """)
    
    with tab4:
        st.header("💾 Export Data")
        
        csv_data = display_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"tennis_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()