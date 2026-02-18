from sentence_transformers import SentenceTransformer, util
import numpy as np
from datetime import datetime
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class ConversationAnalyzer:
    def __init__(self):
        # Load a efficient, small model
        # Using a singleton pattern or global load might be better for performance in prod,
        # but for this local tool, loading in init is acceptable (though it will delay startup slightly)
        print("Loading SentenceTransformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2') 
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        print("Model loaded.")
        
        self.intents = {
            "agreement": ["ok", "sure", "fine", "agreement", "yes", "deal", "k", "acceptable"],
            "passive_ack": ["seen", "hmm", "interesting", "oh", "ah", "noted", "cool"],
            "disinterest": ["whatever", "idk", "maybe later", "busy", "don't care", "meh"],
            "irriation": ["stop", "annoying", "leave me alone", "whatever", "ugh"],
            "urgency": ["asap", "now", "urgent", "emergency", "immediately", "hurry"]
        }
        
        # Pre-compute embeddings for reference intents
        self.intent_embeddings = {
            k: self.model.encode(v) for k, v in self.intents.items()
        }

    def predict_intent(self, text):
        if not text:
            return "unknown", 0.0

        # 1. Heuristics for very short texts
        text_lower = text.lower().strip()
        if text_lower in ["ok", "k", "kk", "thumbs up", "👍", "yep", "yea"]:
            return "agreement", 0.95
        if text_lower in ["hmm", "cool"]:
            return "passive_ack", 0.8
            
        # 2. Semantic Search
        embedding = self.model.encode(text)
        
        best_intent = "neutral"
        max_score = 0.0
        
        for intent, ref_embeddings in self.intent_embeddings.items():
            # Compute cosine similarity
            scores = util.cos_sim(embedding, ref_embeddings)
            # Take the max similarity with any of the reference phrases for this intent
            score = float(scores.max())
            if score > max_score:
                max_score = score
                best_intent = intent
        
        # Threshold for "neutral"
        if max_score < 0.3:
            return "neutral", max_score
            
        return best_intent, max_score

    def calculate_urgency(self, text, time_gap_seconds=None):
        score = 0
        if not text:
            return 0
            
        text_lower = text.lower()
        
        # Linguistic signals
        if "!!" in text: score += 20
        if text.isupper() and len(text) > 4: score += 20
        for trigger in ["asap", "emergency", "now", "urgent"]:
            if trigger in text_lower:
                score += 30
                
        if "?" in text and len(text) < 15: # Short questions like "Where?" "When?"
            score += 10
        
        # Temporal signals
        if time_gap_seconds is not None:
            if time_gap_seconds < 30: # Immediate follow-up
                score += 15
            elif time_gap_seconds > 86400: # Reply after a day usually isn't urgent unless context says so
                score -= 10
        
        return min(100, max(0, score))

    def estimate_engagement(self, messages_data):
        """
        messages_data: list of dicts with 'text', 'sender_id', 'date'
        """
        if not messages_data:
            return 0
        
        # Simple engagement metrics
        total_chars = sum(len(m['text'] or "") for m in messages_data)
        avg_len = total_chars / len(messages_data)
        
        # Response time calculation (if we had proper sender distinction logic here)
        # For now, just simplistic length/frequency
        
        score = min(100, (avg_len / 5) * 10) # 50 chars avg = 100 score
        return score

    def calculate_sentiment(self, text):
        """
        Returns a compound sentiment score between -1 (Negative) and 1 (Positive).
        """
        if not text:
            return 0.0
        scores = self.sentiment_analyzer.polarity_scores(text)
        return scores['compound']

    def analyze_emotional_tone(self, sentiment_score):
        if sentiment_score >= 0.05:
            return "Positive"
        elif sentiment_score <= -0.05:
            return "Negative"
        else:
            return "Neutral"

    def detect_emotional_drift(self, sentiment_scores):
        """
        Analyzes the trend of sentiment scores to detect drift.
        sentiment_scores: List of float scores ordered by time (oldest to newest)
        Returns: "Warming", "Cooling", "Stable", or "Volatile"
        """
        if len(sentiment_scores) < 3:
            return "Stable"
            
        # Simple linear regression slope
        x = np.arange(len(sentiment_scores))
        y = np.array(sentiment_scores)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.05:
            return "Warming"
        elif slope < -0.05:
            return "Cooling"
        else:
            return "Stable"

# Singleton instance
analyzer = ConversationAnalyzer()
