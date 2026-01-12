from transformers import pipeline

# We use a pipeline for easy implementation
# In production, swap 'text-classification' with a specific mental health model
class MoodAnalyzer:
    def __init__(self):
        # Loading a model that detects Negative emotions (Sadness, Fear, etc.)
        # This is the "Detector"
        print("Loading AI Model...")
        self.classifier = pipeline("text-classification", 
                                   model="bhadresh-savani/distilbert-base-uncased-emotion", 
                                   return_all_scores=True)

    def analyze_text(self, text):
        """
        Returns a Risk Score (0 to 1) and a Label.
        Higher score = More Sadness/Fear detected.
        """
        results = self.classifier(text)[0]
        
        # We look specifically for 'sadness' or 'fear' as proxies for depression in this demo
        sadness_score = 0
        label = "Neutral"
        
        for res in results:
            if res['label'] == 'sadness':
                sadness_score = res['score']
                label = "Sadness"
            elif res['label'] == 'fear':
                 # Adding fear to risk but with lower weight
                sadness_score += (res['score'] * 0.5)

        # Cap score at 1.0
        final_score = min(sadness_score, 1.0)
        
        return final_score, label