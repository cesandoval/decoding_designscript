import re, os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments.formatters import RtfFormatter
from pygments.formatters import NullFormatter
from pygments.styles import get_style_by_name
#from pygments.styles import get_all_styles
#styles = list(get_all_styles())
#print styles
from dc_pygments_extensions import *

from dc_svg_writer import *


'''
INDD
'''

do_centcol = True
#do_linenos = False
do_tabcomments = False
# tagged text is in points
# page is 159mm wide
ppmm = 2.83464567 # points per mm
col_a_width = 64 * ppmm
col_b_width = 92 * ppmm
col_c_width = 3 * ppmm # base width from which tabs start, and gaps left in tabs if tab comments
tab_width = 3 * ppmm #CHANGE IN SVG WRITER FILE TOO

max_code_chars = 80
max_comment_chars = 56

def process_all(codestring,indd_tar_file,html_tar_file,xmlstr,lines):
    codes = []
    comments = []
    in_code = True
    for n,line in enumerate(lines):
        if "/*" in line:
            in_code = False
            comments.append([])
            continue
        if "*/" in line:
            in_code = True
            codes.append([])
            continue

        if in_code: codes[-1].append(line)
        else: comments[-1].append(line)
    if len(codes[0]) == 0: codes.pop(0)
    narrative = comments[1:]
    headdict = ''.join(comments[0])
    
    c = 1 # code block num
    htmlstr = open_html(headdict)
    for n, code in enumerate(codes):
        code_block_name = indd_tar_file.split('\\')[-1]+str(c)
        pseudo = False
        if "[pseudo]" in narrative[c-1]:
            print code_block_name, "PSEUDO"
            pseudo = True
        else: print code_block_name
        
        dd = dimension_dict("html")
        clines = []
        # split comments from code
        code_lines, comment_lines, tab_counts = split_comments(''.join(code),xmlstr,c)
        for line, comment, tab in zip(code_lines, comment_lines, tab_counts):
            cline = Codeline(line.strip(),comment,tab)
            clines.append(cline)
        # pseudo
        if pseudo : clines = handle_pseudo(clines)

        # now that pseudo has removed lines, we can assign pos
        assign_positions(clines,dd)

        # TODO
        # break up long def codelines and handle def comments
        clines = handle_split_defs(clines)

        funcs, has_funcs = split_funcs(clines,verbose=False)
        if not has_funcs:
            indented = False
            for n in range(len(clines)):
                if starts_indent(n,clines):
                    indented = True
                    break
            for cline in clines: 
                cline.tab += 1
                cline.pos = (cline.pos[0]+tab_width,cline.pos[1])


        # write to the HTML string
        htmlstr, blockheight = process_html(''.join(narrative[c-1]),clines,code_block_name,c,htmlstr,has_funcs,pseudo)
        c+=1
        
        # close up the HTML and write file
        close_html(htmlstr)
        f = open (html_tar_file+".html", 'w')
        f.write(htmlstr)
        f.close()


'''
HTML
'''

def open_html(headstring):
    str = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd"><html>'
    str += html_head
    str += "<body>"+headstring
    return str

def close_html(htmlstr):
    htmlstr += "</body></html>"
    return htmlstr

html_line_height = 14 # change in SVG writer too
html_cmmt_col_width = 270 # change in SVG writer too (this minus html_tab_width)
html_code_col_width = 480 # change in SVG writer too
html_tab_width = 18 # change in SVG writer too

    
def process_html(narrative,clines,code_block_name,c,htmlstr,has_funcs,pseudo=False):
    htmlstr += "\n<div class='narr_wrap'>"+narrative+"<br><span class='codeblock_name'>"+code_block_name+"</span></div>"
    #htmlstr += "<div style=''"+svg+"</div>"
    svghght = len(clines) * html_line_height
    svgfile = code_block_name.replace('.', '_')
    htmlstr += "<div class='svg_wrap' style='background-image: url("+svgfile+".svg), none; height: "+str(svghght)+"px;'></div>"
    htmlstr += "\n<div class='py_wrap'>\n"
    for cline in clines:
        code = highlight_html(cline.str)
        cmmt = cline.comment
        if cline.code_is_blank : code = "&nbsp;"
        if cline.comment_is_blank: cmmt = "&nbsp;"
        
        # pseudo
        if pseudo and cline.is_pseudo:
            code = "<div class='source'><pre class='pseudo'>"+cmmt+"</pre></div>"
            cmmt = "&nbsp;"
        
        # comment
        pad = 0
        if not has_funcs : pad = html_tab_width * 2 # default padding for comments
        if cline.is_def:
            if not cline.comment_is_blank:
                pad = html_tab_width / 2
                    
        htmlstr += "<div class='cmt_para' style='padding-right:"+str(pad)+"px; width:"+str(html_cmmt_col_width-pad)+"px;'>"+cmmt+"</div>"
        
        # code
        pad = (cline.tab * html_tab_width)
        htmlstr += "<div class='py_para' style='padding-left:"+str(pad)+"px; width:"+str(html_code_col_width-pad)+"px;'>"+code+"</div>"
        #lineno += len(code.splitlines())
    htmlstr += "\n</div>\n"
    return htmlstr, svghght

def process_html_XXXXXXXX(codestring, tar_file):
    headstring, codestring = split_header(codestring)
    codearr = split_sections(codestring)
    if not codearr: str = highlight_html(codestring)
    else:
        #print len(codearr[0]), len(codearr[1]), codearr[0][1][-20:-1]
        str = html_open + headstring + "<table>"
        lineno = 1
        for code, narrative in zip(codearr[0], codearr[1]):
            str += "<tr><td>"+narrative+"</td>"
            str += "<td>"+highlight_html(code,lineno)+"</td></tr>"
            lineno += len(code.splitlines())
        str += "</tr>"+html_close

    f = open (tar_file+".html", 'w') ## a will append, w will over-write
    f.write(str)
    f.close()

def highlight_html(codestring,line_to_start=1):
    return highlight(codestring, DecodesLexer(), HtmlFormatter(style='autumn', full=False, cssclass="source", linenos=False, linenostart=line_to_start))



'''
UTIL
'''
def append_error(xmlstr,msg):
    xmlstr.append('                <error msg="'+msg+'"></error>')




def split_comments(codestring,xmlstr,codeblock_num):

    global cmt
    lines = codestring.splitlines()
    code, comments, tabs = [], [], []
    cmt = ""
    def record_cmt(ln):
        global cmt
        if len(ln) > max_comment_chars : append_error(xmlstr, "FOUND A COMMENT THAT IS TOO LONG in codeblock "+str(codeblock_num)+" max is "+str(max_comment_chars)+" chars")
        if ln == "" : comments.append(" ")
        else : comments.append(ln)
        cmt = ""

    def record_code(ln):
        if len(ln) > max_code_chars : append_error(xmlstr, "FOUND A LINE OF CODE THAT IS TOO LONG in codeblock "+str(codeblock_num)+" max is "+str(max_code_chars)+" chars")

        if "\t" in ln : append_error(xmlstr, "FOUND A LINE OF CODE THAT CONTAINS A TAB - INDENTATION LIKELY INCORRECT in codeblock "+str(codeblock_num))

        leading_spaces = len(ln) - len(ln.lstrip())
        tab_cnt = leading_spaces//4
        tabs.append(tab_cnt)

        if line.strip() == "" :
            code.append("")
        else:
            code.append(ln)

    for line in lines:
        if len(line.strip())>0 and line.strip()[0:2] == "//":
            #suffix = "\b|"*(leading_spaces//4)
            if cmt != "" : append_error(xmlstr,  "FOUND TWO COMMENTS IN A ROW - ignoring the first one in codeblock "+str(codeblock_num))
            #cmt += line.replace("#","").strip()
            cmt = line.replace("//","").strip()
        else:
            record_cmt(cmt)
            record_code(line)

    try:
        while (len(code[0])==0 or code[0].isspace()) and (len(comments[0])==0 or comments[0].isspace()) :
            code = code[1:]
            comments = comments[1:]
            tabs = tabs[1:]
    except:
        raise SyntaxError("unexpected empty codeblock found in codeblock "+str(codeblock_num))

    return code, comments, tabs

def split_sections(codestring):
    arr = re.compile('"""(?s)(.*?)"""').split(codestring)
    if len(arr)==1:
        #print "only found one section, this code doesn't appear to be marked up"
        codearr, narrativearr = [codestring], []
    if len(arr)%2==0:
        print "!!!!!!!!!!!!!!!!!!!!!! an even number of sections were found... what gives?"
        return False
    else:
        codearr = arr[0::2]
        narrativearr = [""]+arr[1::2] # we expect to see code first, not narrative first... even out the lists with an empty narrative, delete later if needed
        if codearr[0].strip() == "" :
            # blank row found
            codearr, narrativearr = codearr[1:], narrativearr[1:]

    return [s.lstrip('\n').rstrip() for s in codearr], [re.sub(' +',' ',s.strip()) for s in narrativearr]

def split_header(codestring):
    arr = re.compile("/*\n(?s)(.*?)\n*/").split(codestring)
    return arr[1],arr[2]

def handle_split_defs(clines):
    retlines = []

    for n,cline in enumerate(clines):
        if cline.is_def:
            if not cline.comment_is_blank:
                pass
                #cline.comment = cline.comment+"     "
            if cline.str.strip()[-1] != ")":
                m = n+1
                while m<len(clines):
                    clines[m]._force_blank = True
                    clines[m].pos = (cline.pos[0],clines[m].pos[1])
                    if len(clines[m].str.strip())>0 and clines[m].str.strip()[-1]==")" : break
                    m += 1
        retlines.append(cline)
    return retlines

def handle_pseudo(clines):
    retlines = []

    for cline in clines:
        if cline.is_blank: retlines.append(cline)

        # eliminate uncommented and unimportant lines
        if not cline.is_def and not cline.is_loop and not cline.is_ifish and cline.comment_is_blank: continue
        retlines.append(cline)

    for cline in retlines:
        # switch to comment as code for any line that has a comment (and is not a 'special case')
        if cline.is_def: continue
        if cline.comment_is_blank: continue
        cline._pseudo = True

    return retlines
    '''
    nlines = []
    for cline in retlines:
        # add blank lines before defs and capitalize comments
        if cline.is_def:
            nlines.append(Codeline("","",cline.tab))

        # capatalize comments??
        #if len(cline.comment)>1 : cline.comment = cline.comment[0].capitalize() + cline.comment[1:]
        nlines.append(cline)


    return nlines
    '''

'''
<tstyle:py_table><tStart:><coStart:<tcaw:170>><coStart:<tcaw:283.5>><rStart:>
<clStart:><pstyle:py_para>one<clEnd:>
<clStart:><pstyle:py_para>two<clEnd:>
<rEnd:><rStart:>
<clStart:><pstyle:py_para>three<clEnd:>
<clStart:><pstyle:py_para>four<clEnd:>
<rEnd:><rStart:>
<clStart:><clEnd:>
<clStart:>
<pstyle:py_para>six
<pstyle:py_para>seven
<pstyle:py_para>vec = Vec(-2*self.rad, 0, 0)*Xform.rotation(angle=f*math.pi/2)
<clEnd:>
<rEnd:><tEnd:>
'''

html_head = """
<head>
  <title></title>
  <meta http-equiv="content-type" content="text/html; charset=None">
  <style type="text/css">

.narr_wrap {
    font-style: italic;
    text-align: center;
    margin-top: 25px;
    margin-bottom: 10px;
    width: 760px;
}
.py_wrap{
    width: 760px;
}

.py_para{
    float:left;
    height: """+str(html_line_height)+"""px;
}

.py_para pre {
    margin: 0px;
    font-family: monospace;
    font-size: 11px;
}

pre {
    /* background-color: #0fd; */
}

.cmt_para{
    float: left;
    height: """+str(html_line_height)+"""px;
    text-align: right;
    overflow: hidden;
    font-family: sans-serif;
    font-size: 12px;
    font-style: italic;
}

/* clearfix */
.py_wrap:after {
   content: " ";
   display: block;
   height: 0;
   clear: both;
}

.svg_wrap{
    position: absolute;
    width: 760px;
    background-repeat: no-repeat;
    background-size: cover;
}



td.linenos { background-color: #f0f0f0; padding-right: 10px; }
span.lineno { background-color: #f0f0f0; padding: 0 5px 0 5px; }
body .hll { background-color: #ffffcc }
body  { background: #ffffff; }
body .c { color: #aaaaaa; font-style: italic } /* Comment */
body .err { color: #F00000; background-color: #F0A0A0 } /* Error */
body .k { color: #0000aa } /* Keyword */
body .cm { color: #aaaaaa; font-style: italic } /* Comment.Multiline */
body .cp { color: #4c8317 } /* Comment.Preproc */
body .c1 { color: #aaaaaa; font-style: italic } /* Comment.Single */
body .cs { color: #0000aa; font-style: italic } /* Comment.Special */
body .gd { color: #aa0000 } /* Generic.Deleted */
body .ge { font-style: italic } /* Generic.Emph */
body .gr { color: #aa0000 } /* Generic.Error */
body .gh { color: #000080; font-weight: bold } /* Generic.Heading */
body .gi { color: #00aa00 } /* Generic.Inserted */
body .go { color: #888888 } /* Generic.Output */
body .gp { color: #555555 } /* Generic.Prompt */
body .gs { font-weight: bold } /* Generic.Strong */
body .gu { color: #800080; font-weight: bold } /* Generic.Subheading */
body .gt { color: #aa0000 } /* Generic.Traceback */
body .kc { color: #0000aa } /* Keyword.Constant */
body .kd { color: #0000aa } /* Keyword.Declaration */
body .kn { color: #0000aa } /* Keyword.Namespace */
body .kp { color: #0000aa } /* Keyword.Pseudo */
body .kr { color: #0000aa } /* Keyword.Reserved */
body .kt { color: #00aaaa } /* Keyword.Type */
body .m { color: #009999 } /* Literal.Number */
body .s { color: #aa5500 } /* Literal.String */
body .na { color: #1e90ff } /* Name.Attribute */
body .nb { color: #00aaaa } /* Name.Builtin */
body .nc { color: #00aa00; text-decoration: underline } /* Name.Class */
body .no { color: #aa0000 } /* Name.Constant */
body .nd { color: #888888 } /* Name.Decorator */
body .ni { color: #800000; font-weight: bold } /* Name.Entity */
body .nf { color: #00aa00 } /* Name.Function */
body .nn { color: #00aaaa; text-decoration: underline } /* Name.Namespace */
body .nt { color: #1e90ff; font-weight: bold } /* Name.Tag */
body .nv { color: #aa0000 } /* Name.Variable */
body .ow { color: #0000aa } /* Operator.Word */
body .w { color: #bbbbbb } /* Text.Whitespace */
body .mf { color: #009999 } /* Literal.Number.Float */
body .mh { color: #009999 } /* Literal.Number.Hex */
body .mi { color: #009999 } /* Literal.Number.Integer */
body .mo { color: #009999 } /* Literal.Number.Oct */
body .sb { color: #aa5500 } /* Literal.String.Backtick */
body .sc { color: #aa5500 } /* Literal.String.Char */
body .sd { color: #aa5500 } /* Literal.String.Doc */
body .s2 { color: #aa5500 } /* Literal.String.Double */
body .se { color: #aa5500 } /* Literal.String.Escape */
body .sh { color: #aa5500 } /* Literal.String.Heredoc */
body .si { color: #aa5500 } /* Literal.String.Interpol */
body .sx { color: #aa5500 } /* Literal.String.Other */
body .sr { color: #009999 } /* Literal.String.Regex */
body .s1 { color: #aa5500 } /* Literal.String.Single */
body .ss { color: #0000aa } /* Literal.String.Symbol */
body .bp { color: #00aaaa } /* Name.Builtin.Pseudo */
body .vc { color: #aa0000 } /* Name.Variable.Class */
body .vg { color: #aa0000 } /* Name.Variable.Global */
body .vi { color: #aa0000 } /* Name.Variable.Instance */
body .il { color: #009999 } /* Literal.Number.Integer.Long */
  </style>
</head>
"""




