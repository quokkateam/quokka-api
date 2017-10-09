from mako.template import Template


def template_as_str(path, vars={}):
  t = Template(filename=path, input_encoding='utf-16', output_encoding='utf-16')
  return t.render(**vars).decode('utf-16').encode('utf8')