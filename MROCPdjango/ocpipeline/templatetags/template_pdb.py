from django.template import Library, Node

register = Library()

try:
    import ipdb as pdb
except ImportError:
    import pdb

class PdbNode(Node):
    def render(self, context):
        pdb.set_trace()
        return ''
      
@register.tag
def pdb_debug(parser, token):
    return PdbNode()
