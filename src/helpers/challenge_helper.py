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

  return formatted_prizes