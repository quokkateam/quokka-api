from datetime import datetime
from src.challenges import universal_challenge_info


def format_challenges(challenges):
  formatted_challenges = []

  for c in challenges:
    universal_challenge = universal_challenge_info.get(c.slug)

    formatted_challenges.append({
      'name': c.name,
      'slug': c.slug,
      'previewText': universal_challenge['preview_text'],
      'points': c.points,
      'startDate': datetime.strftime(c.start_date, '%m/%d/%y'),
      'endDate': datetime.strftime(c.end_date, '%m/%d/%y')
    })

  return formatted_challenges