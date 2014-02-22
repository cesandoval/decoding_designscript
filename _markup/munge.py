import os, re, sys, traceback
from lib.dc_ds_highlighter import *
import shutil

html_path = "_html"
subfolder_name = "_markup"

do_ghx = False

def empty_directory(folder):
    try:
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            if os.path.isfile(file_path): os.unlink(file_path)
    except Exception, e:
        print e
            
def munge_part(part_path,part_title,part_id,xml):
    xml.append("<part title='"+part_title+"' id='"+str(part_id)+"'>")

    for chapter in os.listdir(part_path):
        if os.path.isdir(os.path.join(part_path,chapter)):
            try:
                chapter_id = chapter.split('.')[1][:2]
                chapter_title = chapter.split(' - ')[1]
            except:
                print "could not parse chapter: "+chapter
                continue
            xml.append("    <chapter title='"+chapter_title+"' id='"+chapter_id+"'>")
            print "++++++++++++++",chapter_id,"|",chapter_title ,"++++++++++++++"
            print "+++++++++++++++++++++++++++++++++++++++++++++"
            for folder in os.listdir(os.path.join(part_path,chapter)):
                if re.match(r'\d.\d\d.\D\d\d - ',folder) :
                    files = os.listdir(os.path.join(part_path,chapter,folder))    
                    if any([file.endswith('.ds') for file in files]):
                        example_id = folder.split('.')[2][:3]
                        example_title = folder.split(' - ')[1]
                        xml.append("        <example title='"+example_title+"' id='"+example_id+"'>")
                        print "------",example_id,"|",example_title ,"------"
                        
                        # found folder containing at least one python file
                        dcfolder = os.path.join(part_path,chapter,folder)
                        print dcfolder
                        # prepare markup subfolder
                        subfolder = os.path.join(dcfolder,subfolder_name)
                        if os.path.isdir(subfolder) : empty_directory(subfolder)
                        else : os.makedirs(subfolder)
                        for file in os.listdir(dcfolder):
                            if file.endswith('.ds'):
                                script_id = file.split('.')[2][3:]
                                script_src = file[:-3].replace('.','_')
                                xml.append("            <script id='"+script_id+"' src='"+script_src+".html'>")
                                print "---",file[:-3], "---"
                                try:
                                    with open(os.path.join(dcfolder, file), "r") as f: 
                                        codestring = f.read()
                                    with open(os.path.join(dcfolder, file), "r") as f: lines = f.readlines()
                                    process_all(codestring, os.path.join(subfolder, file[:-3]), os.path.join(html_path, script_src),xml,lines)
                                except Exception,e:
                                    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                                    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                                    xml.append('                <error msg="'+str(e)+'"></error>')
                                    print str(e)
                                    print traceback.format_exc()
                                xml.append("            </script>")
                        xml.append("        </example>")
                        
                        
                    else:
                        print "no ds files found here: ", dcfolder
            xml.append("    </chapter>")
                
    xml.append("</part>")



# empty html markup subfolder
empty_directory(html_path)


# start xml string
xml = ["<examples>"]

munge_part("..\\p4","Part Four",4,xml)

xml.append("</examples>")

f = open ("_data.xml", 'w') ## a will append, w will over-write 
for s in xml: f.write(s+"\n")
f.close()
