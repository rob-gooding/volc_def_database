#!/usr/bin/env python
""" volc_def: a database of volcano deformation
    
    This module contains the code that can be used to
    process files containing information about volcano
    deformation. These can be used, for example, to 
    build a website of observations.
    
    When used as a module a single class is exposed
    which allows objects describing volcano 
    defomation to be created and manipulated
    
    When used as a script, the class is populated
    by reading an file describing a single volcano
    and an operation (validation, converting to
    XML etc.) on the resulting data is undertaken.
    """

import re
import datetime

class Volcano:
    """ A container and processor for volcano defomation """
    
    def __init__(self, filename=None, debug=False):
        # This is called when a new instance of
        # Volcano is created. First set all the 
        # possible data fields to 'null' values
        # so we can tell if data is missing.
        self.id = None
        self.name = None
        self.latitude = float('NaN')
        self.longitude = float('NaN')
        self.rocktype = None
        self.typev = None
        self.region = None
        self.elevation = None
        self.studies = []
        self.events = []
        self.references = []
        self.description = ""
        # NOTE: put new data holders here
        #       choosing a sensible null value
        
        # If we have a filename we can use it 
        # to populate the data now.
        if filename is not None:
            self._parse_file(filename, debug=debug)
    
    def _parse_file(self, filename, debug=False):
        # This is a simple state machine based
        # parser to read our data file format.
        # There are definatly better ways to do this
        # but this is simple!
        
        section_name = None # Are we in a section, which one?
        keyword = None # What is this line's keyword?
        multiline = False
        multiline_keyword = None
        
        f = open(filename, 'r')
        for line in f:
            
            new_section = re.match(r"\s*\[\s*Start\s+(\w+)\s*\]",line)
            if new_section:
                if section_name is None:
                    # New section in root of file... OK
                    section_name = new_section.group(1).strip().upper()
                    # Create new empty object for this section
                    if (section_name=="STUDY"):
                        self.studies.append(Study())
                    elif(section_name=="EVENT"):
                        self.events.append(Event()) 
                    continue 
                else:
                    raise Exception("Sections cannot be nested")
            
            end_section = re.match(r"\s*\[\s*End\s+(\w+)\s*\]",line)
            if end_section:
                if (end_section.group(1).strip().upper()==section_name):
                    # Ended this section OK
                    section_name = None
                    continue
                else:
                    raise Exception("End section did not match start")
            
            key_val = re.match(r"\s*(\w+)\s*:(.+?)$", line)
            if key_val:
                keyword = key_val.group(1).strip().upper()
                value = key_val.group(2).strip()
                if (value==">>"):
                    if multiline:
                        raise Exception("Cannot nest multiline blocks")
                    else:
                        multiline = True
                        multiline_keyword = keyword
                        continue
                elif (value=="<<"):
                    if not multiline:
                        raise Exception("Not in a multiline block")
                    elif (multiline_keyword != keyword):
                        raise Exception("End multiline mismatch")
                    else:
                        multiline = False
                        multiline_keyword = None
                        continue
                else:
                    if section_name is None:
                        # process this keyword value pair
                        # in file root.
                        if keyword=="ID":
                            self.id = value
                            continue
                        elif keyword=="NAME":
                            self.name = value
                            continue
                        elif keyword=="LATITUDE":
                            self.latitude = float(value)
                            continue
                        elif keyword=="LONGITUDE":
                            self.longitude = float(value)
                            continue
                        elif keyword=="ROCKTYPE":
                            self.rocktype = value
                            continue
                        elif keyword=="TYPEV":
                            self.typev = value
                            continue
                        elif keyword=="REGION":
                            self.region = value
                            continue
                        elif keyword=="COUNTRY":
                            self.country = value
                            continue
                        elif keyword=="ELEVATION":
                            self.elevation = value
                            continue  
                        elif keyword=="DESCRIPTION":
                            self.description = self.description+value
                            continue
                        elif keyword=="REFERENCE":
                            self.references.append(value)
                            continue
                        elif keyword=="DOI":
                            self.doi = value
                            continue    
                        
                        else:
                            # Don't recognise this - skip
                            continue
                    elif section_name == "STUDY":
                        if keyword=="TYPE":
                            if self.studies[-1].type is None:
                                self.studies[-1].type = value
                            else:
                                raise Exception("Double study type")
                        elif keyword=="DESCRIPTION":
                            self.studies[-1].description = self.description+value
                            continue
                        elif keyword=="STARTDATE":
                            (d, m, y) = value.split('/',3)
                            self.studies[-1].startdate = datetime.date(int(y), int(m), int(d))
                            continue
                        elif keyword=="ENDDATE":
                            (d, m, y) = value.split('/',3)
                            self.studies[-1].enddate = datetime.date(int(y), int(m), int(d))
                            continue
                        elif keyword=="REFERENCE":
                            self.studies[-1].references.append(value)
                            continue
                    
                    elif section_name == "EVENT":
                        if keyword=="TYPE":
                            if self.event[-1].type is None:
                                self.event[-1].type = vaue
                            else:
                                raise Exception("Double study type")
                        elif keyword=="DESCRIPTION":
                            self.event[-1].description = self.description+value
                            continue
                        elif keyword=="STARTDATE":
                            (d, m, y) = value.split('/',3)
                            self.event[-1].startdate = datetime.date(int(y), int(m), int(d))
                            continue
                        elif keyword=="ENDDATE":
                            (d, m, y) = value.split('/',3)
                            self.event[-1].enddate = datetime.date(int(y), int(m), int(d))
                            continue
                        elif keyword=="REFERENCE":
                            self.event[-1].references.append(value)
                            continue
                    
                    else:
                        raise Exception("In unrecognised section")
            else:
                # Error unless we are in a multilne block
                if multiline:
                    if section_name is None:
                        if multiline_keyword == "DESCRIPTION":
                            self.description = self.description+line.strip()+" "
                    elif section_name == "STUDY":
                        if multiline_keyword == "DESCRIPTION":
                            self.studies[-1].description = self.description+line.strip()+" "
                    elif section_name == "EVENT":
                        if multiline_keyword == "DESCRIPTION":
                            self.event[-1].description = self.description+line.strip()+" "
    
    # Should we error out here? 
    
    def dump(self):
        print "ID: " + self.id
        print "Name: " + self.name
        print "Latitude: " + str(self.latitude)
        print "Longitude: " + str(self.longitude)
        print "Rocktype: " + self.rocktype
        print "Volcano Type:" + self.typev
        print "Region:" + self.region
        print "Country:" + self.country
        print "Elevation:" + self.elevation
        print "DOI:" + self.doi
        print
        if self.description != "":
            print "Description: " + self.description
        
        for event in self.events:
            print "[Start event]"
            print "Type: " + event.type
            if event.description != "":
                print "Description: " + event.description
            if event.startdate is not None:
                print "Startdate: " + event.startdate.strftime('%d/%m/%Y')
            if study.enddate is not None:
                print "Enddate: " + event.enddate.strftime('%d/%m/%Y')
            for reference in event.references:
                print "Reference: " + reference
            print "[End event]"
        
        for study in self.studies:
            print "[Start study]"
            print "Type: " + study.type
            if study.description != "":
                print "Description: " + study.description
            if study.startdate is not None:
                print "Startdate: " + study.startdate.strftime('%d/%m/%Y')
            if study.enddate is not None:
                print "Enddate: " + study.enddate.strftime('%d/%m/%Y')
            for reference in study.references:
                print "Reference: " + reference
            print "[End study]"
        
        for reference in self.references:
            print "Reference: " + reference
    
    def html(self):
        head = """
            <html lang="en">
            <head>
            
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>Volcano Page</title>
            <meta name="Generator" content="Serif WebPlus X6">
            <meta name="viewport" content="width=1200">
            <style type="text/css">
            </style>
           
            <link rel="stylesheet" href="wpscripts/wpstyles.css" type="text/css"></head>
            
            <body text="#000000" style="background:#ffffff; height:1500px;">
            <div style="background-color:transparent;margin-left:auto;margin-right:auto;position:relative;width:1200px;height:1500px;">
            <img src="http://www1.gly.bris.ac.uk/~juliet/About_my_research_files/main_image.jpg" border="0" width="1300" height="1500" alt="" style="position:absolute;left:0px;top:0px;">
            <img src="grey_box.jpg" border="0" width="1150" height="1300" alt="" style="position:absolute;left:25px;top:150px;">
            <div style="position:absolute;left:466px;top:17px;width:445px;height:33px; background-color:#ffffff;">
            <a href="home.html" id="nav_16_B1" class="Button1" style="display:block;position:absolute;left:5px;top:5px;width:141px;height:22px;"><span>Home</span></a>
            <a href="vindex.html" id="nav_16_B2" class="Button1" style="display:block;position:absolute;left:146px;top:5px;width:141px;height:22px;"><span>Volcano&nbsp;Index</span></a>
            <a href="taskforce.html" id="nav_16_B3" class="Button1" style="display:block;position:absolute;left:287px;top:5px;width:141px;height:22px;"><span>Task&nbsp;Force</span></a>
            </div>
            <div style="position:absolute;left:26px;top:8px;width:286px;height:130px;             <p class="Body-P"><span class="Body-C"><img src="gvm_logo_1.png"></span></p>
            </div>
            <div style="position:absolute;left:75px;top:140px;width:1049px;height:1274px; background-color:#fefdf9;background: transparent url('wpimages/wp8eda78db_06.png') no-repeat top left;">
            <img src="http://geology.com/volcanoes/chaiten/chaiten-eruption-column.jpg" border="0" width="391" height="420" alt="" style="position:absolute;left:32px;top:91px;">
            <div style="position:absolute;left:26px;top:560px;width:1003px;height:143px; background-color:#696969; border: 3px solid #000000;overflow:hidden;">
            <p class="Wp-Body-P"><span class="Body-C-C1"><font color="#ffffff"><font face = "Gill Sans MT"><font size = "4">{description}</font></font></font> &nbsp;</span></p>
            </div>
            <div style="position:absolute;left:36px;top:14px;width:906px;height:67px;overflow:hidden;">
            <p class="Wp-Body-P"><span class="Body-C-C2"><font size="20.0 px"><font face="Gill Sans MT">{name}</font></font></span></p>
            </div>
            <div id="map_3" style="position:absolute;left:746px;top:302px;width:280px;height:241px;border:1px solid #979797;background-color:#e5e3df;">
            <div style="padding:1em; color:gray;">Loading...</div>
            </div>
            <table id="table_6" cellspacing="0" cellpadding="0" style=" border-collapse: collapse; position:absolute; left:432px; top:302px; width:308px; height:224px;">
            <col style="width:161px;">
            <col style="width:145px;">
            <tr style="height:45px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C"><font face="Gill Sans MT"><font size="5">Region:</font></font></span></p>
            </td>
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C0"><font face="Arial"><font size="5">{region}</font></font></span></p>
            </td>
            </tr>
            <tr style="height:45px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C"><font face="Gill Sans MT"><font size="5">Country:</font></font></span></p>
            </td>
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C0"><font face="Arial"><font size="5">{country}</font></font></span></p>
            </td>
            </tr>
            <tr style="height:45px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C"><font face="Gill Sans MT"><font size="5">Elevation:</font></font></span></p>
            </td>
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C0"><font face="Arial"><font size="5">{elevation}</font></font></span></p>
            </td>
            </tr>
            <tr style="height:45px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C"><font face="Gill Sans MT"><font size="5">Latitude:</font></font></span></p>
            </td>
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C0"><font face="Arial"><font size="5">{lat}</font></font></span></p>
            </td>
            </tr>
            <tr style="height:45px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C"><font face="Gill Sans MT"><font size="5">Longitude:</font></font></span></p>
            </td>
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C0"><font face="Arial"><font size="5">{lon}</font></font></span></p>
            </td>
            </tr>
            </table>
            <table id="table_7" cellspacing="0" cellpadding="0" style=" border-collapse: collapse; position:absolute; left:432px; top:93px; width:314px; height:196px;">
            <col style="width:313px;">
            <tr style="height:49px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C1"><font face="Gill Sans MT"><font size="5">Name:</font></font></span></p>
            </td>
            </tr>
            <tr style="height:49px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C1"><font face="Gill Sans MT"><font size="5">Volcano ID:</font></font></span></p>
            </td>
            </tr>
            <tr style="height:49px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C1"><font face="Gill Sans MT"><font size="5">Main Rock Type:</font></font></span></p>
            </td>
            </tr>
            <tr style="height:49px;">
            <td style="vertical-align:top; padding:1px 4px 1px 4px;">
            <p class="Wp-Table-Body-P"><span class="Table-Body-C-C1"><font face="Gill Sans MT"><font size="5">Volcano Type:</font></font></span></p>
            </td>
            </tr>
            </table>
            <div style="position:absolute;left:746px;top:93px;width:265px;height:37px; background-color:#636363;overflow:hidden;">
            <p class="Wp-Body-P"><span class="Body-C-C1"><font face="Arial"><font color="#ffffff"><fontsize="30px"><centre>{name}</span></centre></p>
            </div>
            <div style="position:absolute;left:746px;top:143px;width:265px;height:35px; background-color:#636363;overflow:hidden;">
            <p class="Wp-Body-P"><span class="Body-C-C1">{id}</span></p>
            <p class="Wp-Body-P"><span class="Body-C-C3"><br></span></p>
            </div>
            <div style="position:absolute;left:746px;top:239px;width:265px;height:37px; background-color:#636363;overflow:hidden;">
            <p class="Wp-Body-P"><span class="Body-C-C1">{vtype}</span></p>
            </div>
            <div style="position:absolute;left:746px;top:191px;width:265px;height:38px; background-color:#636363;overflow:hidden;">
            <p class="Wp-Body-P"><span class="Body-C-C1">{rock}</font></font></font></span></p>
            <p class="Wp-Body-P"><span class="Body-C-C3"><br></span></p>
            </div>
            <div style="position:absolute;left:100px;top:709px;width:681px;height:47px;overflow:hidden;">
            <p class="Wp-Body-P"><span class="Body-C-C4"><font face = "Gill Sans MT"><font size ="5"> Deformation Studies:</font></font></span></p>
            </div>
            </div>
                      <script type="text/javascript" src="http://maps.google.com/maps/api/js?amp;vs=3.3&sensor=false"></script>
            <script type="text/javascript" src="wpscripts/jsWPGoogleMaps.js"></script>
            <script type="text/javascript">
            wpGMapLoad( 'map_3', 54.9523856906335980, -3.8232421875000000, 5, 0, 1, 1, 1, 1, 0, null, 'Failed to generate Google map.', '<br>Street view is not available at this location.' );
            </script>
            </body>
            </html>
            
            
           
            """.format(name=self.name, id=self.id, vtype=self.typev, region=self.region, country=self.country, elevation=self.elevation, doi=self.doi, lat=self.latitude, lon=self.longitude, rock=self.rocktype, description=self.description)
        
        volc_refs = " "
        for reference in self.references:
            volc_refs = volc_refs + " ".format(ref=reference)
        volc_refs = volc_refs+"</ul>"
        
        studies = "<h2>Studies</h2>"
        for study in self.studies:
            # Do we need to give studies names?
            studies = studies+"""
            
                <div style="position:absolute;left:35px;top:909px;width:1001px;height:83px; background-color:#a9a9a9;overflow:hidden;">
                <p class="Wp-Body-P"><span class="Body-C-C5">{desc}</span></p>
                </div>
                </div>
                
                <table id="table_10" cellspacing="0" cellpadding="0" style=" border-collapse: collapse; position:absolute; left:110px; top:910px; width:1001px; height:132px;">
                <col style="width:149px;">
                <col style="width:135px;">
                <col style="width:159px;">
                <col style="width:220px;">
                <col style="width:181px;">
                <col style="width:154px;">
                <tr style="height:53px;">
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C2">Study No.</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C3">DOI</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C3">Type</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C3">Reference</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C3">Start Date</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C3">End Date</span></p>
                </td>
                </tr>
                <tr style="height:78px;">
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C4">#</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C4">DOI</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C4">{type}</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C4">{ref}</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C4">{start}</span></p>
                </td>
                <td style="vertical-align:top; padding:1px 4px 1px 4px; border:2px solid #000000;">
                <p class="Table-Body-P"><span class="Table-Body-C-C4">{end}</span></p>
                </td>
                </tr>
                </table>
                </div>

                                
               """.format(type=study.type,
                                        start=str(study.startdate), 
                                        end=str(study.enddate), 
                                        desc=study.description, ref=reference)
            studies = studies+"  "
            for reference in study.references:
                studies = studies + " ".format(ref=reference)
            studies = studies+" "
        
        events = "<h2> </h2>"
        for event in self.events:
            # Do we need to give events names?
            events = events+"""

                
             
                """.format(type=event.type,
                                        start=str(event.startdate), 
                                        end=str(event.enddate), 
                                        desc=event.description)
            eventss = eventss+" "
            for reference in event.references:
                events = events + " ".format(ref=reference)
            events = events+"</ul>"
        
        tail = "</body></html>"
        return head+events+studies+volc_refs+tail

class Event:
    "Something that happened to a volcano"
    
    def __init__(self):
        self.type = None
        self.description = ""
        self.reference = None
        self.startdate = None
        self.enddate = None
        self.references = []

class Study:
    "An observation of volcanic deformation"
    
    def __init__(self):
        self.type = None
        self.description = ""
        self.reference = None
        self.startdate = None
        self.enddate = None
        self.references = []

if __name__=="__main__":
    import sys
    mode = sys.argv[1]
    for file in sys.argv[2:]:
        volcano = Volcano(filename=file)
        if mode == "dump":
            volcano.dump()
        if mode == "html":
            print volcano.html()





