from pygments.formatter import Formatter
from pygments.style import Style
from pygments.lexers import PythonLexer
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic


class DecodesLexer(PythonLexer):
    
    tokens = PythonLexer.tokens
    tokens['builtins'].append((r'(?<!\.)(Geometry|Vector|Point|Mesh|Line|Ray|PLine|Circle|Arc|Plane|Polygon|Curve|CoordinateSystem|Color|Interval|Xform|Circle'r')\b', Name.Builtin.Decodes))
    #tokens['root'].append((r'(?<!\.)(GREATER|Vec'r')\b', Operator))
    tokens['builtins'].append((r'(GREATER_THAN|LESS_THAN)\b', Operator))
    
    
    def __init__(self, **options):
        PythonLexer.__init__(self, **options)
     
     

class DecodesHTMLStyle(Style):
    #autumn
    #manni
    #perldoc
    default_style = ""
    styles = {
        Comment:      '#666', # single-line comments
        Keyword:                '#00f',
        #Name:                   '#000003',
        Name.Function:          '#00f',
        Name.Class:             '#00f',

        Number:                 '#00f',
        Name.Builtin:           '#00f',
        Name.Builtin.Pseudo:    '#00f',
        Name.Builtin.Decodes:    '#f00',
        
        String:                 '#999999' # seems to apply to both strings and multiline comments

    }

