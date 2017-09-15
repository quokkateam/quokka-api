from datetime import datetime, date
from src.challenges import universal_challenge_info


def format_challenges(challenges, user, curr_week_num=None):
  formatted_challenges = []

  i = 1
  for c in challenges:
    universal_challenge = universal_challenge_info.get(c.slug)

    data = {
      'name': c.name,
      'slug': c.slug,
      'previewText': universal_challenge['preview_text'],
      'startDate': datetime.strftime(c.start_date, '%m/%d/%y'),
      'endDate': datetime.strftime(c.end_date, '%m/%d/%y')
    }

    # Prevent points from being disclosed if week not available yet
    if not curr_week_num or i <= curr_week_num or user.is_admin:
      data['points'] = c.points

    formatted_challenges.append(data)
    i += 1

  return formatted_challenges


def current_week_num(challenges):
  today = date.today()
  launch_date = challenges[0].start_date.date()
  finish_date = challenges[-1].end_date.date()

  # If the challenge hasn't even launched yet, return week 1
  if today < launch_date:
    return 1

  # If the challenge is over, return the last week number
  if today > finish_date:
    return len(challenges)

  # Otherwise, iterate through the challenge date ranges and find which week today lies in
  i = 1
  for c in challenges:
    start_date = c.start_date.date()
    end_date = c.end_date.date()

    if start_date <= today <= end_date:
      return i