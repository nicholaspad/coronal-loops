import warnings
warnings.filterwarnings("ignore", message = "divide by zero encountered in log")
warnings.filterwarnings("ignore", message = "From scipy 0.13.0, the output shape of")
warnings.filterwarnings("ignore", message = "invalid value encountered in greater")
warnings.filterwarnings("ignore", message = "invalid value encountered in less")
warnings.filterwarnings("ignore", message = "invalid value encountered in log")
warnings.filterwarnings("ignore", message = "invalid value encountered in multiply")
warnings.filterwarnings("ignore", message = "numpy.dtype size changed")
from IPython.core import debugger; debug = debugger.Pdb().set_trace

import argparse
import pandas as pd
import xml.etree.cElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument("-id")
id = parser.parse_args().id

if id is None:
	print "Specify event code with -id <code>"
	quit()

spec = pd.read_csv("VOEvent_Spec.txt", skiprows = 2)
vals = spec[id]
params = spec["Parameter"]
categories = spec["VOParamType"]
source = spec["Source"]
r_o = spec["R/O"]

voe = ET.Element("voe:VOEvent")
voe_info = ET.Comment("This is a VOEvent, generated from the annotation process")
voe.insert(1, voe_info)
voe.set("xmlns:voe", "http://www.ivoa.net/xml/VOEvent/v1.1")
voe.set("xmlns:stc", "http://www.ivoa.net/xml/STC/stc-v1.30.xsd")
voe.set("xmlns:lmsal", "http://www.lmsal.com/helio-informatics/lmsal-v1.0.xsd")
voe.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
voe.set("xmlns:crd", "urn:nvo-coords")
voe.set("role", "observation")
voe.set("version", "1.1")
voe.set("xsi:schemaLocation", "http://www.ivoa.net/xml/VOEvent/v1.1 http://www.lmsal.com/helio-informatics/VOEvent-v1.1.xsd")
voe.set("ivorn", "")

# ************ WHO ************ #
Who = ET.SubElement(voe, "Who")
who_info = ET.Comment("Data pertaining to curation")
Who.insert(1, who_info)

AuthorIVORN = ET.SubElement(Who, "AuthorIVORN")
Author = ET.SubElement(Who, "Author")
contactName = ET.SubElement(Author, "contactName") # 1
contactEmail = ET.SubElement(Author, "contactEmail")
contactPhone = ET.SubElement(Author, "contactPhone")
Date = ET.SubElement(Who, "Date")

# TO SET

AuthorIVORN.text = "-"
contactName.text = "-"
contactEmail.text = "-"
contactPhone.text = "-"
Date.text = "-"

# ************ WHAT ************ #
What = ET.SubElement(voe, "What")
what_info = ET.Comment("Data about what was measured/observed")
What.insert(1, what_info)

Description = ET.SubElement(What, "Description") # 1

What_Group_Required = ET.SubElement(What, "Group") # 1
What_Group_Required.set("name", "%s_required" % vals[0])
for i in range(1, len(vals)):
	if vals[i] == "9" and categories[i] == "what":
		t = ET.SubElement(What_Group_Required, "Param")
		t.set("name", params[i].upper())

		# TO SET
		t.set("value", "-")

What_Group_Optional = ET.SubElement(What, "Group") # 1
What_Group_Optional.set("name", "%s_optional" % vals[0])
for i in range(1, len(vals)):
	if vals[i] == "5" and categories[i] == "what":
		t = ET.SubElement(What_Group_Optional, "Param")
		t.set("name", params[i].upper())

		# TO SET
		t.set("value", "-")

# ************ WHERE-WHEN ************ #
WhereWhen = ET.SubElement(voe, "WhereWhen")
where_when_info = ET.Comment("Data pertaining to where and when something occurred")
WhereWhen.insert(1, where_when_info)

ObsDataLocation = ET.SubElement(WhereWhen, "ObsDataLocation") # 1
ObsDataLocation.set("xmlns", "http://www.ivoa.net/xml/STC/stc-v1.30.xsd")

ObservatoryLocation = ET.SubElement(ObsDataLocation, "ObservatoryLocation") # 2
ObservatoryLocation_AstroCoordSystem = ET.SubElement(ObservatoryLocation, "AstroCoordSystem") # 3

ObservatoryLocation_AstroCoords = ET.SubElement(ObservatoryLocation, "AstroCoords") # 3
ObservatoryLocation_AstroCoords.set("id", "UTC-HPC-TOPO")
ObservatoryLocation_AstroCoords.set("coord_system_id", "UTC-HPC-TOPO")

ObservationLocation = ET.SubElement(ObsDataLocation, "ObservationLocation") # 2
ObservationLocation_AstroCoordSystem = ET.SubElement(ObservationLocation, "AstroCoordSystem") # 3

ObservationLocation_AstroCoords = ET.SubElement(ObservationLocation, "AstroCoords") # 3
ObservationLocation_AstroCoords.set("coord_system_id", "UTC-HPC-TOPO")

Time = ET.SubElement(ObservationLocation_AstroCoords, "Time") # 4
TimeInstant = ET.SubElement(Time, "TimeInstant") # 5
TimeInstant_ISOTime = ET.SubElement(TimeInstant, "ISOTime") # 6

Position2D = ET.SubElement(ObservationLocation_AstroCoords, "Position2D") # 4
Value2 = ET.SubElement(Position2D, "Value2") # 5
Position2D_Value_C1 = ET.SubElement(Value2, "C1") # 6
Position2D_Value_C2 = ET.SubElement(Value2, "C2") # 6
Error2 = ET.SubElement(Position2D, "Error2") # 5
Position2D_Error_C1 = ET.SubElement(Error2, "C1") # 6
Position2D_Error_C2 = ET.SubElement(Error2, "C2") # 6
AstroCoordArea = ET.SubElement(ObservationLocation, "AstroCoordArea") # 3
TimeInterval = ET.SubElement(AstroCoordArea, "TimeInterval") # 4
StartTime = ET.SubElement(TimeInterval, "StartTime") # 5
StartTime_ISOTime = ET.SubElement(StartTime, "ISOTime") # 6
StopTime = ET.SubElement(TimeInterval, "StopTime") # 5
StopTime_ISOTime = ET.SubElement(StopTime, "ISOTime") # 6
Box2 = ET.SubElement(AstroCoordArea, "Box2") # 4
Center = ET.SubElement(Box2, "Center") # 5
Box_Center_C1 = ET.SubElement(Center, "C1") # 6
Box_Center_C2 = ET.SubElement(Center, "C2") # 6
Size = ET.SubElement(Box2, "Size") # 5
Box_Size_C1 = ET.SubElement(Size, "C1") # 6
Box_Size_C2 = ET.SubElement(Size, "C2") # 6

# WhereWhen_Group_Required = ET.SubElement(WhereWhen, "Group") # 1
# WhereWhen_Group_Required.set("name", "%s_required" % vals[0])
# for i in range(1, len(vals)):
# 	if vals[i] == "9" and categories[i] == "wherewhen":
# 		t = ET.SubElement(WhereWhen_Group_Required, "Param")
# 		t.set("name", params[i].upper())
# 		t.set("value", "-")

WhereWhen_Group_Optional = ET.SubElement(WhereWhen, "Group") # 1
WhereWhen_Group_Optional.set("name", "%s_optional" % vals[0])
for i in range(1, len(vals)):
	if vals[i] == "5" and categories[i] == "wherewhen":
		t = ET.SubElement(WhereWhen_Group_Optional, "Param")
		t.set("name", params[i].upper())
		t.set("value", "-")

# TO SET

ObservationLocation.set("id", "-")
TimeInstant_ISOTime.text = "-"
Position2D.set("unit", "-")
Position2D_Value_C1.text = "-"
Position2D_Value_C2.text = "-"
Position2D_Error_C1.text = "-"
Position2D_Error_C2.text = "-"
StartTime_ISOTime.text = "-"
StopTime_ISOTime.text = "-"
Box_Center_C1.text = "-"
Box_Center_C2.text = "-"
Box_Size_C1.text = "-"
Box_Size_C2.text = "-"

# ************ HOW ************ #
How = ET.SubElement(voe, "How")
how_info = ET.Comment("Data pertaining to how the feature/event detection was performed")
How.insert(1, how_info)

lmsal_data = ET.SubElement(How, "lmsal:data") # 1
for i in range(1, len(source)):
	if source[i] == "data" and categories[i] == "how" and r_o[i] == "r":
		t = ET.SubElement(lmsal_data, "%s" % params[i])

		# TO SET
		t.text = "-"

lmsal_method = ET.SubElement(How, "lmsal:method") # 1
for i in range(1, len(source)):
	if source[i] == "method" and categories[i] == "how" and r_o[i] == "r":
		if params[i] != "FRM_URL":
			t = ET.SubElement(lmsal_method, "%s" % params[i])
			t.text = "-"
How_Group = ET.SubElement(How, "Group") # 1
How_Group.set("name", "%s_optional" % vals[0])

for i in range(1, len(vals)):
	if vals[i] == "5" and categories[i] == "how":
		t = ET.SubElement(How_Group, "Param")
		t.set("name", params[i].upper())

		# TO SET
		t.set("value", "-")

# ************ WHY ************ #
Why = ET.SubElement(voe, "Why")
Inference = ET.SubElement(Why, "Inference") # 1
Concept = ET.SubElement(Why, "Concept") # 1
Concept.text = "%s" % vals[0]
lmsal_EVENT_TYPE = ET.SubElement(Why, "lmsal:EVENT_TYPE") # 1
lmsal_EVENT_TYPE.text = "%s: %s" % (id, vals[0])
Description = ET.SubElement(Why, "Description") # 1

Why_Group = ET.SubElement(Why, "Group") # 1
Why_Group.set("name", "%s_optional" % vals[0])
for i in range(1, len(vals)):
	if vals[i] == "5" and categories[i] == "why":
		t = ET.SubElement(Why_Group, "Param")
		t.set("name", params[i].upper())

		# TO SET
		t.set("value", "-")

# TO SET

Why.set("importance", "-")
Inference.set("probability", "-")
Description.text = "-"

# ************ CITATIONS ************ #
Citations = ET.SubElement(voe, "Citations")
Citations_Reference_1 = ET.SubElement(Citations, "Reference") # 1

# LIST OF CITATIONS

# ************ OTHER REFERENCES ************ #
Reference_Event_MapURL = ET.SubElement(voe, "Reference")
Reference_FRM_URL = ET.SubElement(voe, "Reference")

Reference_Event_MapURL.set("name", "Event_MapURL")
Reference_FRM_URL.set("name", "FRM_URL")

# TO SET

Reference_Event_MapURL.set("uri", "-")
Reference_FRM_URL.set("uri", "-")

def indent(elem, level = 0):
	i = "\n" + level * "	"
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "	"
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level + 1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

indent(voe)
tree = ET.ElementTree(voe)

tree.write("output.xml")
