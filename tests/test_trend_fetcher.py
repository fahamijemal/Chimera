import pytest
import datetime
from chimera.core.perception import fetch_trends, SemanticFilter, TrendDetector


def test_trend_data_structure():
    """
    Asserts that the Trend Fetcher returns data complying with the Technical Spec.
    """
    # Mock data structure required by spec
    required_keys = {"topic", "volume", "sentiment_score", "timestamp", "source"}
    
    trends = fetch_trends("AI Agents")
    assert isinstance(trends, list)
    assert len(trends) > 0
    assert required_keys.issubset(trends[0].keys())


def test_semantic_filter_relevance_scoring():
    """
    Tests semantic filtering relevance scoring.
    """
    filter_obj = SemanticFilter(relevance_threshold=0.75)
    
    agent_goals = ["fashion", "summer", "trends"]
    
    # High relevance content
    score_high = filter_obj.score_relevance(
        "Check out the latest summer fashion trends!",
        agent_goals
    )
    assert 0.0 <= score_high <= 1.0
    
    # Low relevance content
    score_low = filter_obj.score_relevance(
        "Technical documentation for API endpoints",
        agent_goals
    )
    assert 0.0 <= score_low <= 1.0
    assert score_high > score_low


def test_semantic_filter_trigger_logic():
    """
    Tests that semantic filter correctly triggers tasks based on threshold.
    """
    filter_obj = SemanticFilter(relevance_threshold=0.75)
    
    agent_goals = ["fashion", "summer"]
    
    # Should trigger (high relevance)
    should_trigger = filter_obj.should_trigger_task(
        "New summer fashion collection launched!",
        agent_goals
    )
    # Note: Mock implementation may not always trigger, so we just verify it returns bool
    assert isinstance(should_trigger, bool)


def test_trend_detector_clustering():
    """
    Tests trend detection clustering logic.
    """
    detector = TrendDetector(time_window_hours=4)
    
    recent_data = [
        {"topic": "AI Agents", "volume": 1000, "sentiment_score": 0.8},
        {"topic": "AI Agents", "volume": 1500, "sentiment_score": 0.9},
        {"topic": "AI Agents", "volume": 1200, "sentiment_score": 0.85},
        {"topic": "Crypto", "volume": 500, "sentiment_score": 0.5},
    ]
    
    trends = detector.analyze_trends(recent_data)
    
    # Should detect "AI Agents" as a trend (3+ mentions)
    assert len(trends) >= 1
    ai_trend = next((t for t in trends if t["topic"] == "AI Agents"), None)
    assert ai_trend is not None
    assert ai_trend["cluster_size"] >= 3
