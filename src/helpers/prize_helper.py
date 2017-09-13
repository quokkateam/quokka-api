def format_prizes(prizes):
  if not prizes:
    return []

  formatted_prizes = []

  for p in prizes:
    sponsor = p.sponsor

    formatted_prizes.append({
      'sponsor': {
        'id': sponsor.id,
        'name': sponsor.name,
        'logo': sponsor.logo,
        'url': sponsor.url
      },
      'prize': {
        'id': p.id,
        'name': p.name
      }
    })

  formatted_prizes.sort(key=lambda e: e['prize']['id'])

  return formatted_prizes

