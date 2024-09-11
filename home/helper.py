def get_result(normalized_score):
    if normalized_score > 80:
        return {'score': normalized_score, 'text': 'Advanced', 'color': '#32EE32', 'class':'success'}
    elif 60 < normalized_score <= 80:
        return {'score': normalized_score, 'text': 'Average', 'color': '#004400', 'class':'primary'}
    elif 40 < normalized_score <= 60:
        return {'score': normalized_score, 'text': 'Basic', 'color': '#FFA400', 'class':'warning'}
    else:
        return {'score': normalized_score, 'text': 'Weak', 'color': '#FF0000', 'class':'danger'}

def get_result_text(normalized_score):
    return get_result(normalized_score)['text']

def get_recommendations(normalized_score):
    recommendations = []
    if normalized_score < 80:
        recommendations = [
            "Implement stronger password policies",
            "Conduct regular security audits",
            "Enhance staff training on cybersecurity best practices",
            # ... (rest of the recommendations)
        ]
        return recommendations

