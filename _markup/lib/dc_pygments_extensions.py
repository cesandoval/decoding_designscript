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
     
     
class DecodesInddStyle(Style):
    default_style = ""
    styles = {
        Comment:                '#000001', # single-line comments
        Keyword:                 '#000002',
        #Name:                   '#000003',
        Name.Function:         '#000004',
        Name.Class:             '#000005',

        Number:                 '#100001',
        Name.Builtin:                 '#100002',
        Name.Builtin.Pseudo:      '#100003',
        Operator:                       '#100004',
        
        Name.Builtin.Decodes:    '#000000',
        String:                 '#999999' # seems to apply to both strings and multiline comments

    }
    
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

class InddFormatter(Formatter):

    def __init__(self, **options):
        Formatter.__init__(self, **options)

        # create a dict of (start, end) tuples that wrap the
        # value of a token so that we can use it in the format
        # method later
        self.styles = {}

        # we iterate over the `_styles` attribute of a style item
        # that contains the parsed style values.
        for token, style in self.style:
            start = end = ''
            if style['color']:
                sty = str(style['color'])
                if sty == "000000": start, end = '<cstyle:py_decodes>','<cstyle:>'
                if sty == "000001": start, end = '<cstyle:py_comment>','<cstyle:>'
                elif sty == "000002": start, end = '<cstyle:py_keyword>','<cstyle:>'
                elif sty == "000003": start, end = '<cstyle:py_name>','<cstyle:>'
                elif sty == "000004": start, end = '<cstyle:py_name_func>','<cstyle:>'
                elif sty == "000005": start, end = '<cstyle:py_name_class>','<cstyle:>'
                
                elif sty == "100001": start, end = '<cstyle:py_number>','<cstyle:>'   
                elif sty == "100002": start, end = '<cstyle:py_builtin>','<cstyle:>'   
                elif sty == "100003": start, end = '<cstyle:py_builtin>','<cstyle:>'  
                elif sty == "100004": start, end = '<cstyle:py_operator>','<cstyle:>'  
                
                elif sty == "999999": start, end = '<cstyle:py_string>','<cstyle:>'
                #else : start, end = '<cstyle:py_default>','<cstyle:>'
                
            self.styles[token] = (start, end)

    def format(self, tokensource, outfile):
        # lastval is a string we use for caching
        # because it's possible that an lexer yields a number
        # of consecutive tokens with the same token type.
        # to minimize the size of the generated html markup we
        # try to join the values of same-type tokens here
        lastval = ''
        lasttype = None

        # wrap the whole output with <pre>
        #outfile.write('<ASCII-WIN>\n')

        for ttype, value in tokensource:
            # if the token type doesn't exist in the stylemap
            # we try it with the parent of the token type
            # eg: parent of Token.Literal.String.Double is
            # Token.Literal.String
            while ttype not in self.styles:
                ttype = ttype.parent
            if ttype == lasttype:
                # the current token type is the same of the last
                # iteration. cache it
                lastval += value
            else:
                # not the same token as last iteration, but we
                # have some data in the buffer. wrap it with the
                # defined style and write it to the output file
                if lastval:
                    stylebegin, styleend = self.styles[lasttype]
                    outfile.write(stylebegin + lastval + styleend)
                # set lastval/lasttype to current values
                lastval = value
                lasttype = ttype

        # if something is left in the buffer, write it to the
        # output file, then close the opened <pre> tag
        if lastval:
            stylebegin, styleend = self.styles[lasttype]
            outfile.write(stylebegin + lastval + styleend)
        #outfile.write('</pre>\n')
        