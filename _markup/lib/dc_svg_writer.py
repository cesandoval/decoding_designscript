import pysvg
for subpackage in ['core', 'filter', 'gradient', 'linking', 'script','shape','structure','style','text', 'builders']:
    exec 'import pysvg.' + subpackage
    exec 'from pysvg.' + subpackage + ' import *'

'''
ppmm = 2.83464567 # points per mm
row_height = 2.20 * ppmm
tab_width = 3 * ppmm #CHANGE IN HIGHLIGHTER FILE TOO
x_spine = (64+1.5) * ppmm - 8
'''

#ppmm = -1
row_height = -1
tab_width = -1
x_spine = -1
rad_dot = -1
rad_dotdef = -1
do_multiline = False


def dimension_dict(mode):
    #global row_height
    #global tab_width
    #global x_spine
    #global rad_dot
    #global rad_dotdef
    ret = {}
    if mode == "indd" : 
        ppmm = 2.83464567
        ret['row_height'] = 2.20 * ppmm
        ret['rad_dot'] = 0.4*ppmm
        ret['rad_dotdef'] = 0.75*ppmm
        ret['x_spine'] = (64+1.5) * ppmm - 8
        ret['tab_width'] = 3 * ppmm
        
    if mode == "html" : 
        ppmm = 6.36
        ret['row_height'] = 2.20 * ppmm
        ret['rad_dot'] = 0.4*ppmm
        ret['rad_dotdef'] = 0.75*ppmm
        ret['x_spine'] = 290-(18*1.25) # if html column widths adjusted, change here
        ret['tab_width'] = 18
    
    return ret
    

sty_dot = StyleBuilder()
sty_dot.setStrokeWidth(0)
sty_dot.setFilling('black')

sty_dotdef = StyleBuilder()
sty_dotdef.setStrokeWidth(0)
sty_dotdef.setFilling('black')

sty_normal_line = StyleBuilder()
normal_line_weight = 1.0
sty_normal_line.setStrokeWidth(normal_line_weight)
sty_normal_line.setStroke('black')

sty_normal_line_half = StyleBuilder()
normal_line_half_weight = 0.5
sty_normal_line_half.setStrokeWidth(normal_line_weight)
sty_normal_line_half.setStroke('black')

#double_line_offset = rad_dot*0.5
double_line_offset = 2.83464567 * 0.4 * 0.5 # match rad_dot
dobule_line_weight = 0.5
sty_double_line = StyleBuilder()
sty_double_line.setStrokeWidth(dobule_line_weight)
sty_double_line.setStroke('black')

triple_line_offset = double_line_offset
triple_line_weight = 0.25
sty_triple_line = StyleBuilder()
sty_triple_line.setStrokeWidth(triple_line_weight)
sty_triple_line.setStroke('black')

sty_loop_line = StyleBuilder()
sty_loop_line.setStrokeWidth(0.25)
sty_loop_line.setStroke('black')

sty_if_line = StyleBuilder()
if_line_weight = 0.5
sty_if_line.setStrokeWidth(if_line_weight)
sty_if_line.setStroke('black')

sty_if_tail = StyleBuilder()
sty_if_tail.setStrokeWidth(if_line_weight)
sty_if_tail.setStroke('black')
syy_if_tail_dasharr = [if_line_weight,if_line_weight] # dashed style set at time when line is drawn
#sty_if_tail.setStrokeLineCap('round')

textstyle=StyleBuilder()
textstyle.setFontFamily(fontfamily="Verdana")
textstyle.setFontSize(str(9.25)) #no need for the keywords all the time

def redimension(mode):
    if mode == "indd" : ppmm = 2.83464567
    if mode == "html" : ppmm = 6.36
    
    global row_height
    row_height = 2.20 * ppmm
    
    global tab_width
    tab_width = 3 * ppmm
    if mode == "html" : tab_width = 18
    
    global x_spine
    x_spine = (64+1.5) * ppmm - 8
    if mode == "html" : x_spine = 270-(18*1.25)
    
    global rad_dot
    rad_dot = 0.4*ppmm
    
    global rad_dotdef
    rad_dotdef = 0.75*ppmm


"""
def draw_to_svg(clines,s,xmlstr,mode):
    #print 'svg ',id
    redimension(mode)
    
    funcs, has_funcs = split_funcs(clines,xmlstr)
    #print clines
    #print funcs
    for flines in funcs:
        flines = count_loops(flines)
        #print '',flines[0].row_num, '-', flines[-1].row_num, has_funcs
        #print flines[0]
        
        draw_dots(flines,s) # draw dots
        draw_loops(flines,s) # draw loops
        draw_ifelse(flines,s,xmlstr) # draw if-else
        draw_lines(flines,s) # draw lines


            
def draw_ifelse(clines,s,xmlstr=False):
    # given lines of code, draws if-then-else-elif graphics where appropriate
    # codes lines will arrive in groups of functional code-blocks
    # and have access to the following properties:
    # row_num - the number of the row of this line of code within the larger code-block (that contains multiple functions)
    # tab - the number of tabs for this line of code
    # pt - a tuple position related to this line of code
    hrh = row_height / 2
    htw = tab_width / 2
    ifblocks = []
    for n, cline in enumerate(clines):
        if cline.str.startswith(('if')):
        #if starts_indent(n,clines) and cline.str.startswith(('if')):
            # find the structure of this if statement
            idx, ended = [n], False
            for m in range(n+1,len(clines)):
                if (not clines[m].is_blank) and clines[m].tab <= cline.tab :
                    if clines[m].str.startswith(('else')) or clines[m].str.startswith(('elif')):
                        idx.append(m)
                    else: 
                        idx.append(m)
                        ended = True
                        break
            # cull if statements that do not involve indentation
            if any([starts_indent(i,clines) for i in idx]):
                if not ended: idx.append(-1)
                ifblocks.append(idx)
            else:
                # here's where we catch a series of single-line if-elif-else
                for i in idx: draw_dot(clines[i].pos,s)
            
    for ifb in ifblocks:
        # the first index of the ifblock is the if-statement
        # each additional index is an elif or an else
        # the last index is the first non-blank line that follows the if-block
        # if the last index is -1, the if-block terminates at the end of this codeblock
        #print ifb
        #for idx in ifb: print clines[idx]
        ifline = clines[ifb[0]]
        
        # draw if diamond and connector
        draw_diamond(ifline.pos,s)
        nline = next_codeline(ifb[0],clines)
        if starts_indent(ifb[0],clines) and nline : draw_joiner_line((nline.pos[0],ifline.pos[1]),nline.pos,s,ifline.loopcnt)
        
        endline = clines[ifb[-1]] # the next line of code following this if-block
        terminal = ifb[-1] == -1
        
        # left vert line
        if ifb[-1] != -1:
            yline = prev_codeline(ifb[1],clines)
            draw_if_line(endline.pos,(endline.pos[0],yline.pos[1]+hrh),s,style="tail")
            
        # right vert line
        if len(ifb)==2: 
            # is a if statement on its own
            if ifb[-1] != -1 : 
                # if statement is indented, and followed by more code
                yline = prev_codeline(ifb[-1],clines)
                draw_if_line((ifline.pos[0]+htw,ifline.pos[1]),(ifline.pos[0]+htw,yline.pos[1]+hrh/2),s)
        else:
            yline = clines[ifb[-2]]
            draw_if_line((ifline.pos[0]+htw,ifline.pos[1]),(yline.pos[0]+htw,yline.pos[1]),s)
            
        # for each thing besides the first
        for idx in ifb[1:]:
            if idx >= 0:
                line = clines[idx]
                pline = prev_codeline(idx,clines)
                nline = next_codeline(idx,clines)
               #print ifline, nline
                if not nline:
                    pass
                    # TODO: this is catching the wrong error
                    #if xmlstr : append_error(xmlstr,"IF-ELSE STATEMENT FOUND WITH INCONSISTANT INDENTATION -to work graphically, if one block of statement is indented, then all blocks must be.  "+ifline.str)
                else:
                    if line.str.startswith(('else')) :
                        # draw else dot and diag connector
                        pos = (line.pos[0]+htw,line.pos[1])
                        draw_dot(pos,s)
                        if starts_indent(idx,clines): 
                            draw_joiner_line(pos,nline.pos,s) 
                        else:
                            # this is a single-line else terminating an indented if
                            line.connect_to_me = False
                    if line.str.startswith(('elif')) :
                        draw_diamond(line.pos,s,style="half")
                        pos = (line.pos[0]+tab_width,line.pos[1])
                        if starts_indent(idx,clines): 
                            draw_joiner_line(pos,nline.pos,s) 
                        else:
                            # this is a single-line elif 
                            line.connect_to_me = False
                            
                # if the ifblock does not terminate the codeblock, draw tail lines
                if not terminal:
                    # check for single-line else and elif statements
                    if not pline.connect_to_me:
                        if pline.str.startswith(('elif')) :draw_if_line((pline.pos[0]+tab_width,pline.pos[1]),(endline.pos[0],pline.pos[1]+hrh),s,style="tail")
                        if pline.str.startswith(('else')) :draw_if_line((pline.pos[0]+htw,pline.pos[1]),(endline.pos[0],pline.pos[1]+hrh/2),s,style="tail")
                    else:
                        if pline.tab == endline.tab + 1 : 
                            #print "tab....",line
                            draw_if_line(pline.pos,(endline.pos[0],pline.pos[1]+hrh),s,style="tail")
                        else :
                            #print "-----",line
                            draw_if_line((endline.pos[0]+tab_width,pline.pos[1]),pline.pos,s,style="tail")
                            draw_if_line((endline.pos[0]+tab_width,pline.pos[1]),(endline.pos[0],pline.pos[1]+hrh),s,style="tail")
                        
     
def draw_loops(clines,s):
    # given lines of code, draws loop graphics where appropriate
    # codes lines will arrive in groups of functional code-blocks
    # and have access to the following properties:
    # row_num - the number of the row of this line of code within the larger code-block (that contains multiple functions)
    # tab - the number of tabs for this line of code
    # pt - a tuple position related to this line of code
    for n, cline in enumerate(clines):
        if cline.is_loop:
            #print cline
            nline = next_codeline(n,clines)
            if not nline : continue
            if cline.tab == nline.tab: continue
            draw_loop(cline,nline,s)
            
            # if this isn't a directly nested loop, find where loop returns and draw loop line
            pline = prev_codeline(n,clines)
            if pline and not pline.is_loop:
                returned = False
                for m in range(n+1,len(clines)):
                    if clines[m].is_blank: continue
                    if clines[m].tab > cline.tab: continue
                    if clines[m].tab == cline.tab: draw_loop_line(cline.pos,clines[m].pos,s) # loop returns to same indentation
                    else: draw_loop_line(cline.pos,(cline.pos[0],clines[m-1].pos[1]),s) #loop returns to lower indentation
                    returned = True
                    break
                if not returned : 
                    #draw_loop_line(cline.pos,(cline.pos[0],clines[len(clines)-1].pos[1]),s) #loop ends with eof
                    pass
                    
def draw_dots(clines,s):
    # given lines of code, draws dots where appropriate
    # codes lines will arrive in groups of functional code-blocks
    # and have access to the following properties:
    # row_num - the number of the row of this line of code within the larger code-block (that contains multiple functions)
    # tab - the number of tabs for this line of code
    # pt - a tuple position related to this line of code
    no_dot_keywords = ('if','else','elif')
    
    for n, cline in enumerate(clines):
        if cline.is_blank: continue
        if cline.str.startswith(no_dot_keywords): continue
        if cline.is_def: 
            draw_dot(cline.pos,s,style='def')
            continue
            
        draw_dot(cline.pos,s)
            
def draw_lines(clines,s,xmlstr=False):
    # given lines of code, draws regular line connections where appropriate
    # codes lines will arrive in groups of functional code-blocks
    # and have access to the following properties:
    # row_num - the number of the row of this line of code within the larger code-block (that contains multiple functions)
    # tab - the number of tabs for this line of code
    # pt - a tuple position related to this line of code
    for n, cline in enumerate(clines):
        pline = prev_codeline(n,clines)
        
        
        if cline.is_def: 
            #print cline
            #print len(clines), n
            try:
                draw_joiner_line(cline.pos,clines[n+1].pos,s) # draw diagonal line
                nline = next_codeline(n,clines)
                if nline and nline.pos[1] != clines[n+1].pos[1]:
                    draw_joiner_line(clines[n+1].pos,nline.pos,s) # draw vertical line if line is blank
                continue
            except:
               if xmlstr : append_error(xmlstr,"Found a single-line def statement... check on how this file has been blocked")
               return
               #raise SyntaxError("Found a single-line def statement... check on how this file has been blocked")
        
        
        if not pline : continue
        if cline.is_blank : continue
        if pline.tab != cline.tab: continue # if tab of previous codeline changes tabs
        if cline.str.startswith(('else')) and starts_indent(n,clines): continue
        if not pline.connect_to_me: continue
        #if pline.str.startswith(('else')) : continue # if previous line starts with else (which must mean this is a single-line else)
        #if cline.is_blank and cline.tab != next_codeline(n,clines).tab : continue # if this is a blank line, and the next line changes tab SUPERSEDED by above
        draw_joiner_line(cline.pos,pline.pos,s,cline.loopcnt)  
   
   
def next_codeline(n,clines):
    # returns the next valid line of code, skipping over blank lines
    for m in range(n+1,len(clines)):
        if not clines[m].is_blank : return clines[m]
    #print "next_codeline could not find another line of code"
    return False
        
def prev_codeline(n,clines):
    # returns the prev valid line of code, skipping over blank lines
    for m in range(n-1,-1,-1):
        if not clines[m].is_blank : return clines[m]
    #print "prev_codeline could not find another line of code", n, range(n-1,-1,-1)
    return False

"""    

def starts_indent(n,clines):
    #returns true if line n comes just before an indented code block
    for m in range(n+1,len(clines)):
        if not clines[m].code_is_blank : break
        
    try:
        if clines[n].tab < clines[m].tab : return True
    except:
        pass
    return False
"""
'''
def ends_indent(n,clines):
    #returns true if line n comes at the end of an indented code block
    try:
        if clines[n].tab > clines[n+1].tab  : return True
    except:
        pass
    return False
'''

def count_loops(clines):
    # adds a property loopcnt to each line in clines
    # that describes how many loops it is nested within
    
    loops = [] # an array of (si,ei) of each loop
    for n in range(len(clines)):
        if clines[n].is_loop and starts_indent(n,clines):
            found_end = False
            for m in range(n+1,len(clines)):
                if clines[m].tab == clines[n].tab :
                    found_end = True
                    loops.append((n,m-1))
                    #n = m
                    break
            if not found_end:
                loops.append((n,len(clines)-1))
                #break
                
     # ensure that no loops end in blank lines
    for n in range(len(loops)):
        while clines[loops[n][1]].is_blank:
            loops[n] = (loops[n][0],loops[n][1]-1)
            
    for n in range(len(clines)):
        clines[n].loopcnt = 0
        for loop in loops:
            if n > loop[0] and n <= loop[1] :
                clines[n].loopcnt += 1
    #print loops
    return clines
"""

def split_funcs(clines,xmlstr=False,verbose=False):
    # splits given code lines into blocks defined by functions
    # used only at the top level for each codeblock
    funcs = []
    for n in range(len(clines)):
        if clines[n].is_def and starts_indent(n,clines):
            #print 'starting at',clines[n].str
            found_end = False
            for m in range(n+1,len(clines)):
                if clines[m].tab == clines[n].tab and not clines[m].code_is_blank:
                    found_end = True
                    funcs.append((n,m-1))
                    n = m
                    break
            if not found_end:
                #print "noend"
                funcs.append((n,len(clines)-1))
                break
    
     # ensure that no funcs end in blank lines
    for n in range(len(funcs)):
        while clines[funcs[n][1]].code_is_blank:
            funcs[n] = (funcs[n][0],funcs[n][1]-1)
        
    # if no funcs were found,
    if len(funcs)==0 : 
        return[clines], False

    
    code_before = funcs[0][0]!=0
    code_after = funcs[-1][1] != len(clines)-1
    # catches code blocks before all def statements
    if code_before and any(not line.code_is_blank for line in clines[:funcs[0][0]-1]):
        funcs.insert(0,(0,funcs[0][0]-1))
        if verbose: print funcs
        
    # catches code blocks after all def statements
    if code_after and any(not line.code_is_blank for line in clines[funcs[-1][1]+1:]):
        funcs.append((funcs[-1][1]+1,len(clines)-1))
        if verbose: print funcs   
            
    #TODO, collect loose blocks between defs
    
    '''
        raise_error = False
        if funcs[0][0]!=0:
            # found loose code at start of codeblock
            # TODO go through all lines prior to start of first func
            #
            if not clines[0].str.startswith('class') and not clines[0].str.startswith('@'):
                raise_error = True
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", clines[0].str
        if funcs[-1][1] != len(clines)-1:
            # found loose code at end of codeblock
            raise_error = True

        if raise_error and xmlstr: append_error(xmlstr,"FUNCTION DEFINITIONS CANNOT BE MIXED WITH LOOSE CODE")
        '''
        
    #print funcs, clines[funcs[0][0]].row_num, clines[funcs[0][1]].row_num
    return [[clines[n] for n in range(func[0],func[1]+1)] for func in funcs], True
   
def assign_positions(clines,dd):
    for n,cline in enumerate(clines):
        #print n, tab
        x = dd['x_spine'] + cline.tab * dd['tab_width']
        y = (dd['row_height']/2)+dd['row_height']*n
        
        if cline.is_def : x += tab_width/2
        
        cline.pos = ((x,y))
        
"""  
def draw_dot(p,s,style='normal'):
    oh = ShapeBuilder()
    
    if style == 'def':
        cir = oh.createCircle(p[0],p[1], rad_dotdef)
        cir.set_style(sty_dotdef.getStyle())
    elif style == 'if':
        cir = oh.createCircle(p[0],p[1], double_line_offset + dobule_line_weight/2 )
        cir.set_style(sty_dot.getStyle())
    else:
        cir = oh.createCircle(p[0],p[1], rad_dot)
        cir.set_style(sty_dot.getStyle())
    
    s.addElement(cir)
   
def draw_loop(line,nline,s):
    if do_multiline : 
        off = normal_line_weight/2
        oh = ShapeBuilder()
        lines = []
        p0 = line.pos
        p1 = nline.pos
        off = double_line_offset+dobule_line_weight/2
        line = oh.createLine(p0[0], p0[1], p1[0]+off, p0[1]) # horz line
        line.set_style(sty_normal_line.getStyle())
        lines.append(line)
        
        draw_joiner_line((p1[0],p0[1]),p1,s,nline.loopcnt) # vert line
        
        for line in lines: s.addElement(line)
    else:
        oh = ShapeBuilder()
        p0 = line.pos
        p2 = nline.pos
        p1 = (p2[0],p0[1])
        pointsAsTuples=[p0,p1,p2]
        corner = oh.createPolyline(points=oh.convertTupleArrayToPoints(pointsAsTuples),strokewidth=normal_line_weight, stroke='black')
        s.addElement(corner)
    
    
   
def draw_loop_line(p0,p1,s):
    oh = ShapeBuilder()
    lines = []
    off = row_height *0.5
    
    line = oh.createLine(p0[0], p0[1]+off, p1[0], p1[1]-off)
    line.set_style(sty_loop_line.getStyle())
    s.addElement(line)
        
def draw_if_line(p0,p1,s,style='normal'):
    import math
    length = math.sqrt((p0[0]-p1[0])**2+(p0[1]-p1[1])**2)
    #print length, length//sum(syy_if_tail_dasharr), length/(length//sum(syy_if_tail_dasharr))
    cnt = length//sum(syy_if_tail_dasharr) - 0.5
    dasharr = [dim/sum(syy_if_tail_dasharr)*(length/cnt) for dim in syy_if_tail_dasharr]
    
    oh = ShapeBuilder()
    sty_if_tail.setStrokeDashArray(','.join(map(str, dasharr)))
    
    line = oh.createLine(p0[0], p0[1], p1[0], p1[1])
    if style == "tail" : line.set_style(sty_if_tail.getStyle())
    else: line.set_style(sty_if_line.getStyle())
    s.addElement(line)
        
def draw_joiner_line(p0,p1,s,loopcnt=0):  
    #print p0,p1,loopcnt
    oh = ShapeBuilder()
    lines = []
    if loopcnt == 0 or not do_multiline: 
        line = oh.createLine(p0[0], p0[1], p1[0], p1[1])
        line.set_style(sty_normal_line.getStyle())
        lines.append(line)
        
    elif loopcnt ==1 : 
        off = double_line_offset
        line = oh.createLine(p0[0]-off, p0[1], p1[0]-off, p1[1])
        line.set_style(sty_double_line.getStyle())
        lines.append(line)
        
        line = oh.createLine(p0[0]+off, p0[1], p1[0]+off, p1[1])
        line.set_style(sty_double_line.getStyle())
        lines.append(line)
        
    elif loopcnt >=2 : 
        off = triple_line_offset
        
        line = oh.createLine(p0[0], p0[1], p1[0], p1[1])
        line.set_style(sty_triple_line.getStyle())
        lines.append(line)
        
        line = oh.createLine(p0[0]-off, p0[1], p1[0]-off, p1[1])
        line.set_style(sty_triple_line.getStyle())
        lines.append(line)
        
        line = oh.createLine(p0[0]+off, p0[1], p1[0]+off, p1[1])
        line.set_style(sty_triple_line.getStyle())
        lines.append(line)
        
    else:
        pass
        
    for line in lines: s.addElement(line)
   
def draw_diamond(pos, s,style='normal'):
    oh = ShapeBuilder()
    htw = tab_width / 2
    hgt = row_height *0.5
    off = (double_line_offset + dobule_line_weight/2)
    if not do_multiline : off = normal_line_weight/2
    p0 = [pos[0]-off,pos[1]]
    p1 = [pos[0]+htw,pos[1]+hgt/2]
    p2 = [pos[0]+tab_width+off,pos[1]]
    p3 = [pos[0]+htw,pos[1]-hgt/2]
    pointsAsTuples=[p0,p1,p2,p3,p0]  
    if style=='half' : 
        p1[0] -= if_line_weight/2
        p3[0] -= if_line_weight/2
        pointsAsTuples=[p1,p2,p3,p1]
    diamond = oh.createPolygon(points=oh.convertTupleArrayToPoints(pointsAsTuples),strokewidth=0, stroke='black', fill='black')
    s.addElement(diamond)
    
    #draw_dot(p0,s,style="if")"""
    
class Codeline():
    def __init__(self,codestring,comment,tab,rownum=-1):
        self.str = codestring
        self.row_num = rownum
        self.tab = tab
        self.comment = comment
        self._continuing = False
        self._pseudo = False
        self._connect_to_me = True
    
    def __repr__(self): return self.str
    
    @property
    def is_continuing_line_above(self):
         return self._continuing
    
    @property
    def connect_to_me(self):
         return self._connect_to_me
         
    @property
    def dont_dot_me(self):
        if self.is_class: return True
        if self.is_decorator: return True
        if self.is_ifish: return True
        if self.is_continuing_line_above: return True
        if self.code_is_blank: return True
        return False
    
    @property
    def code_is_blank(self):
         return self.str == "" or self.str.isspace() or len(self.str.strip())==0
    
    @property
    def comment_is_blank(self):
         return self.comment == "" or self.comment.isspace()
    
    @property
    def is_decorator(self):
        return self.str.startswith('@')
        
    @property
    def is_def(self):
        return self.str.startswith('def')
        
    @property
    def is_class(self):
        return self.str.startswith('class')
        
    @property
    def is_loop(self):
        return self.str.startswith(('for','while'))
        
    @property
    def is_ifish(self):
        return self.str.startswith(('if','else','elif'))
        
    @property
    def maintain_for_pseudo(self):
        # returns true if this line should never be replaced by a comment or eliminated during a pseudo
        return  self.is_def or self.is_loop or self.is_ifish or self.is_decorator or self.is_class
        
    @property
    def is_pseudo(self):
        return self._pseudo
        
    @property
    def continues_to_next(self):
        return self.str.strip().endswith('\\')
 
def append_error(xmlstr,msg):
    xmlstr.append('                <error msg="'+msg+'"></error>')
    
    


