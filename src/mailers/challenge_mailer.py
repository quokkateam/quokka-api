from src.mailers.client import send_email


def weekly_challenge(school=None, delay=True):
  # calculate week_index from today's date
  week_index = 0
  week_num = week_index + 1

  return send_email(
    to='benwhittle31@gmail.com',
    subject='Week {} Challenge'.format(week_num),
    delay=delay
  )