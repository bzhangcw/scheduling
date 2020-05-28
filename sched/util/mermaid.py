from typing import *

import jinja2 as jin

from .io import UTIL_ASSET_PATH

MERMAID_GANTT_HEADER = [
  "gantt",
  "dateFormat YYYY-MM-DD HH:mm:ss",
  "axisFormat %X"
]


def render_meimaid_html(
    record_path: str,
    record_ls: Optional[List] = None,
    template_path: str = f'{UTIL_ASSET_PATH}/mermaid.template',
    fp: str = 'result.html'):
  """
  :param record_path:
  :param record_ls:
  :param template_path:
  :param fp:
  :return:
  """
  env = jin.Environment(loader=jin.FileSystemLoader(['/', './']))
  template = env.get_template(template_path)

  if record_ls is not None:
    record = "\n".join(record_ls)
  else:
    with open(record_path, 'r') as f:
      record = "".join(i for i in f)

  content = template.render(record_path=record_path,
                            record=record)
  with open(fp, 'w') as f:
    f.write(content)

  return content


def bom_to_graph_mermaid(bom: Dict[Tuple, float]):
  """
  ```{=mermaid graph}
  graph TD
    B --> |0.1| C
    C --> D[Laptop]
    C --> E[iPhone]
    C --> F[fa:fa-car Car]
  :param bom:
  :return:
  """

  def generate_graph():
    # ==== sections ====
    yield f"graph TD"
    for (pa, child), v in bom.items():
      yield f"\t{pa} -.-> | %.2f |{child}" % v

  data = generate_graph()
  return data


if __name__ == '__main__':
  render_meimaid_html(template_path=f'{UTIL_ASSET_PATH}/gantt.template',
                      record_path='result/example/gantt.record',
                      fp='result/gantt.html')
