"""
graph/state.py
──────────────────────────────────────────────────
Defines the shared State for the NIVESH agent graph.

Industry standard:
- State is defined ONCE and imported by all agents
- Every field is typed — no surprises at runtime
- Optional fields use None as default — not empty strings
"""

from typing import TypedDict, Optional


class NiveshState(TypedDict):
    user_input: str                             # raw input from user e.g. "Reliance"
    symbol: str                                 # resolved NSE symbol e.g. "RELIANCE"
    stock_data: Optional[str]                   # raw price + basic info
    fundamental_analysis: Optional[str]         # fundamental agent output
    technical_analysis: Optional[str]           # technical agent output
    news_analysis: Optional[str]                # news + sentiment output
    peer_analysis: Optional[str]                # peer comparison output
    final_report: Optional[str]                 # full research report
    recommendation: Optional[str]               # BUY / HOLD / SELL
    error: Optional[str]                        # any error message
    current_agent: Optional[str]                # which agent is running right now


def get_initial_state(user_input: str, symbol: str)-> NiveshState:
    """
        Returns a clean initial state for a new analysis.
        Always start from this — never build state manually.

        Industry standard:
        - One function to create initial state
        - All optional fields start as None
        - Prevents KeyError bugs later
        """
    return NiveshState(
        user_input=user_input,
        symbol=symbol,
        stock_data=None,
        fundamental_analysis=None,
        technical_analysis=None,
        news_analysis=None,
        peer_analysis=None,
        final_report=None,
        recommendation=None,
        error=None,
        current_agent=None,
    )
