from operator import itemgetter

def format_sponsors(sponsors):
  if not sponsors:
    return []

  formatted_sponsors = []

  for s in sponsors:
    formatted_sponsors.append({
      'id': s.id,
      'name': s.name,
      'logo': s.logo,
      'url': s.url
    })

  return sorted(formatted_sponsors, key=itemgetter('name'))
