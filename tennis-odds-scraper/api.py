"""
FastAPI REST API for Tennis Odds Data
Provides RESTful endpoints for accessing scraped tennis odds data.
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uvicorn

from scrapers import OddsportalScraper
from utils import calculate_implied_probability, calculate_bookmaker_margin
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="Tennis Odds API",
    description="RESTful API for tennis betting odds data collection and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response validation
class Match(BaseModel):
    """Tennis match with odds"""
    timestamp: str = Field(..., description="Timestamp of data collection")
    bookmaker: str = Field(..., description="Bookmaker name")
    tournament: str = Field(..., description="Tournament name")
    player1: str = Field(..., description="First player name")
    player2: str = Field(..., description="Second player name")
    odds_player1: float = Field(..., description="Decimal odds for player 1", gt=0)
    odds_player2: float = Field(..., description="Decimal odds for player 2", gt=0)
    implied_prob1: Optional[float] = Field(None, description="Implied probability for player 1 (%)")
    implied_prob2: Optional[float] = Field(None, description="Implied probability for player 2 (%)")
    bookmaker_margin: Optional[float] = Field(None, description="Bookmaker margin (%)")
    match_date: Optional[str] = Field(None, description="Match date")
    match_time: Optional[str] = Field(None, description="Match time")
    url: Optional[str] = Field(None, description="URL to match details")


class Statistics(BaseModel):
    """Overall statistics"""
    total_matches: int
    unique_tournaments: int
    unique_bookmakers: int
    avg_odds: float
    avg_margin: float
    min_margin: float
    max_margin: float
    best_value_matches: List[Dict]


class Tournament(BaseModel):
    """Tournament information"""
    name: str
    url: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None


# Helper functions
def enrich_match_data(matches: List[Dict]) -> List[Dict]:
    """Add calculated fields to match data"""
    for match in matches:
        match['implied_prob1'] = calculate_implied_probability(match['odds_player1'])
        match['implied_prob2'] = calculate_implied_probability(match['odds_player2'])
        match['bookmaker_margin'] = calculate_bookmaker_margin(
            match['odds_player1'],
            match['odds_player2']
        )
    return matches


def scrape_latest_odds(bookmaker: str = 'oddsportal') -> List[Dict]:
    """Scrape latest odds from bookmaker"""
    if bookmaker.lower() == 'oddsportal':
        with OddsportalScraper() as scraper:
            matches = scraper.scrape_tennis_matches()
        return enrich_match_data(matches)
    else:
        raise ValueError(f"Unsupported bookmaker: {bookmaker}")


# API Endpoints
@app.get("/", tags=["Root"])
def root():
    """API root endpoint"""
    return {
        "message": "Tennis Odds API - v1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "matches": "/matches",
            "tournaments": "/tournaments",
            "stats": "/stats",
            "best_value": "/best-value",
            "player": "/player/{player_name}"
        }
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get(
    "/matches",
    response_model=List[Match],
    tags=["Matches"],
    summary="Get all tennis matches",
    description="Retrieve all scraped tennis matches with optional filters"
)
def get_matches(
    bookmaker: str = Query(
        'oddsportal',
        description="Bookmaker to scrape from",
        enum=['oddsportal']
    ),
    tournament: Optional[str] = Query(
        None,
        description="Filter by tournament name (case-insensitive partial match)"
    ),
    min_odds: Optional[float] = Query(
        None,
        description="Minimum odds threshold",
        ge=1.0
    ),
    max_margin: Optional[float] = Query(
        None,
        description="Maximum bookmaker margin (%)",
        ge=0,
        le=20
    ),
    limit: Optional[int] = Query(
        None,
        description="Limit number of results",
        ge=1,
        le=100
    )
):
    """
    Get tennis matches with optional filters.
    
    **Example:**
    ```
    GET /matches?tournament=ATP&max_margin=5.0&limit=10
    ```
    """
    try:
        matches = scrape_latest_odds(bookmaker)
        
        if not matches:
            raise HTTPException(status_code=404, detail="No matches found")
        
        # Apply filters
        if tournament:
            matches = [
                m for m in matches
                if tournament.lower() in m['tournament'].lower()
            ]
        
        if min_odds is not None:
            matches = [
                m for m in matches
                if m['odds_player1'] >= min_odds or m['odds_player2'] >= min_odds
            ]
        
        if max_margin is not None:
            matches = [
                m for m in matches
                if m.get('bookmaker_margin', 100) <= max_margin
            ]
        
        # Apply limit
        if limit:
            matches = matches[:limit]
        
        return matches
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/tournaments",
    response_model=List[Tournament],
    tags=["Tournaments"],
    summary="Get available tournaments"
)
def get_tournaments(
    bookmaker: str = Query('oddsportal', enum=['oddsportal'])
):
    """
    Get list of available tennis tournaments.
    """
    try:
        if bookmaker == 'oddsportal':
            with OddsportalScraper() as scraper:
                tournaments = scraper.get_available_tournaments()
            return tournaments
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported bookmaker: {bookmaker}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/stats",
    response_model=Statistics,
    tags=["Statistics"],
    summary="Get overall statistics"
)
def get_statistics(
    bookmaker: str = Query('oddsportal', enum=['oddsportal'])
):
    """
    Get comprehensive statistics about current odds data.
    """
    try:
        matches = scrape_latest_odds(bookmaker)
        
        if not matches:
            raise HTTPException(status_code=404, detail="No matches found")
        
        df = pd.DataFrame(matches)
        
        # Calculate statistics
        stats = {
            "total_matches": len(df),
            "unique_tournaments": int(df['tournament'].nunique()),
            "unique_bookmakers": int(df['bookmaker'].nunique()),
            "avg_odds": float(df[['odds_player1', 'odds_player2']].mean().mean()),
            "avg_margin": float(df['bookmaker_margin'].mean()),
            "min_margin": float(df['bookmaker_margin'].min()),
            "max_margin": float(df['bookmaker_margin'].max()),
            "best_value_matches": df.nsmallest(5, 'bookmaker_margin')[[
                'player1', 'player2', 'tournament', 'bookmaker_margin'
            ]].to_dict('records')
        }
        
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/best-value",
    response_model=List[Match],
    tags=["Matches"],
    summary="Get best value matches"
)
def get_best_value_matches(
    bookmaker: str = Query('oddsportal', enum=['oddsportal']),
    limit: int = Query(10, description="Number of matches to return", ge=1, le=50)
):
    """
    Get matches with the lowest bookmaker margins (best value).
    """
    try:
        matches = scrape_latest_odds(bookmaker)
        
        if not matches:
            raise HTTPException(status_code=404, detail="No matches found")
        
        # Sort by margin and take top N
        sorted_matches = sorted(
            matches,
            key=lambda x: x.get('bookmaker_margin', 100)
        )
        
        return sorted_matches[:limit]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/player/{player_name}",
    response_model=List[Match],
    tags=["Players"],
    summary="Get matches for a specific player"
)
def get_player_matches(
    player_name: str = Path(..., description="Player name to search for"),
    bookmaker: str = Query('oddsportal', enum=['oddsportal'])
):
    """
    Get all matches for a specific player (case-insensitive search).
    
    **Example:**
    ```
    GET /player/Djokovic
    ```
    """
    try:
        matches = scrape_latest_odds(bookmaker)
        
        if not matches:
            raise HTTPException(status_code=404, detail="No matches found")
        
        # Filter matches containing player name
        player_matches = [
            m for m in matches
            if player_name.lower() in m['player1'].lower() or
               player_name.lower() in m['player2'].lower()
        ]
        
        if not player_matches:
            raise HTTPException(
                status_code=404,
                detail=f"No matches found for player: {player_name}"
            )
        
        return player_matches
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/tournament/{tournament_name}",
    response_model=List[Match],
    tags=["Tournaments"],
    summary="Get matches from a specific tournament"
)
def get_tournament_matches(
    tournament_name: str = Path(..., description="Tournament name"),
    bookmaker: str = Query('oddsportal', enum=['oddsportal'])
):
    """
    Get all matches from a specific tournament.
    
    **Example:**
    ```
    GET /tournament/ATP Australian Open
    ```
    """
    try:
        matches = scrape_latest_odds(bookmaker)
        
        if not matches:
            raise HTTPException(status_code=404, detail="No matches found")
        
        # Filter by tournament
        tournament_matches = [
            m for m in matches
            if tournament_name.lower() in m['tournament'].lower()
        ]
        
        if not tournament_matches:
            raise HTTPException(
                status_code=404,
                detail=f"No matches found for tournament: {tournament_name}"
            )
        
        return tournament_matches
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/arbitrage",
    tags=["Analysis"],
    summary="Find arbitrage opportunities"
)
def find_arbitrage_opportunities(
    bookmaker: str = Query('oddsportal', enum=['oddsportal']),
    min_profit: float = Query(0.0, description="Minimum profit % to show", ge=0)
):
    """
    Find potential arbitrage betting opportunities.
    
    Note: This requires data from multiple bookmakers. Currently returns
    matches with margins close to 100% that could become arbitrage opportunities
    with better odds from other bookmakers.
    """
    try:
        matches = scrape_latest_odds(bookmaker)
        
        if not matches:
            raise HTTPException(status_code=404, detail="No matches found")
        
        # Find matches with very low margins (potential arbitrage)
        arbitrage_candidates = [
            m for m in matches
            if m.get('bookmaker_margin', 100) < 2.0  # Very low margin
        ]
        
        return {
            "message": "Arbitrage detection requires multiple bookmaker data",
            "low_margin_matches": arbitrage_candidates,
            "note": "These matches have low margins and might offer arbitrage when combined with other bookmakers"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc.detail)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )


# Run server
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
