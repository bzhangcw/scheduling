import jinja2 as jin

from .io import UTIL_ASSET_PATH

MERMAID_GANTT_HEADER = [
   "gantt",
   "dateFormat YYYY-MM-DD HH:mm:ss",
   "axisFormat %X"
]


def render_gantt_html(template_path, record_path, fp='result/gantt.html'):
   env = jin.Environment(loader=jin.FileSystemLoader('/'))
   template = env.get_template(template_path)
   with open(record_path, 'r') as f:
      record = "".join(i for i in f)

   content = template.render(record_path=record_path,
                             record=record)
   with open(fp, 'w') as f:
      f.write(content)

   return content


if __name__ == '__main__':
   render_gantt_html(template_path=f'{UTIL_ASSET_PATH}/gantt.template',
                     record_path='result/example/gantt.record',
                     fp='result/gantt.html')
