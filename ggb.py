#!/usr/bin/env python3
import cgi
import cgitb
cgitb.enable()
import io, zipfile, tempfile
import xml.etree.ElementTree as ET
from math import sqrt,atan2,pi
from latex import unicode_to_latex
print('Content-type: text/html; charset=utf-8\n')

post = cgi.FieldStorage(keep_blank_values=True)
z=zipfile.ZipFile(io.BytesIO(post['ggb'].value),"r")
if not 'geogebra.xml' in z.namelist():
	print('Sorry, but your file does not contain "geogebra.xml".')
temp_dir=tempfile.TemporaryDirectory()
z.extract('geogebra.xml',temp_dir.name)
root=ET.parse(temp_dir.name+'/geogebra.xml').getroot()
f=["\\documentclass{standalone}\n\\usepackage{tikz}\n\\begin{document}\n\\begin{tikzpicture}\n\\tikzset{every path/.append style={line width=1}}\n\\pgfmathsetmacro{\pointsize}{.05pt}"]
for pt in root.find("construction").findall("element[@type='point']"):
	if pt.find("coords").attrib["x"]=='NaN' or  pt.find("coords").attrib["y"]=='NaN':
		continue
	pt.find("coords").attrib["x"]=str(float(pt.find("coords").attrib["x"])/float(pt.find("coords").attrib["z"]))
	pt.find("coords").attrib["y"]=str(float(pt.find("coords").attrib["y"])/float(pt.find("coords").attrib["z"]))
for li in root.find("construction").findall("command[@name='Polygon']"):
	se=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	if li.find("input").attrib["a2"].isnumeric():
		pts=[li.find("input").attrib["a0"],li.find("input").attrib["a1"]]+list(li.find("output").attrib.values())[1+int(li.find("input").attrib["a2"]):2*int(li.find("input").attrib["a2"])-1]
		for n,v in li.find("output").attrib.items():
			if n=="a0" or int(n[1:])>int(li.find("input").attrib["a2"]):
				continue
			com=ET.SubElement(root.find("construction"),"command")
			com.set("name","Segment")
			ipt=ET.SubElement(com,"input")
			ipt.set("a0",pts[int(n[1:])-1])
			if n=="a"+li.find("input").attrib["a2"]:
				ipt.set("a1",li.find("output").attrib["a1"])
			else:
				ipt.set("a1",pts[int(n[1:])])
			opt=ET.SubElement(com,"output")
			opt.set("a0",v)
			root.find("construction").find('element[@label="'+v+'"]').find("show").set("object","false")
			root.find("construction").find('element[@label="'+v+'"]').find("show").set("label","false")
		for n,v in li.find("output").attrib.items():
			if int(n[1:])<=int(li.find("input").attrib["a2"]):
				continue
			pt=root.find("construction").find('element[@label="'+v+'"]')
			if n=="a"+str(1+int(li.find("input").attrib["a2"])):
				pt1=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
				pt2=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
				f.append("\n\\draw[color=brown,fill=brown,fill opacity=0.2]("+pt1.find("coords").attrib["x"]+","+pt1.find("coords").attrib["y"]+")--("+pt2.find("coords").attrib["x"]+","+pt2.find("coords").attrib["y"]+")--("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")")
				continue
			f.append("--("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")")
		f.append("--cycle;")
		if se.find("show").attrib["label"]=="true":
			f.append("\n\\draw node")
			if len(se.findall("labelOffset")):
				f.append("[xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
			f.append(" at("+str(sum([float(root.find("construction").find('element[@label="'+v+'"]').find("coords").attrib["x"]) for v in pts])/len(pts))+","+str(sum([float(root.find("construction").find('element[@label="'+v+'"]').find("coords").attrib["y"]) for v in pts])/len(pts))+"){$"+unicode_to_latex(li.find("output").attrib["a0"])+"$};")
	else:
		for n,v in li.find("input").attrib.items():
			pt=root.find("construction").find('element[@label="'+v+'"]')
			if n=="a0":
				f.append("\n\\draw[color=brown,fill=brown,fill opacity=0.2]("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")")
				continue
			f.append("--("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")")
		f.append("--cycle;")
		if se.find("show").attrib["label"]=="true":
			f.append("\\draw node")
			if len(se.findall("labelOffset")):
				f.append("[xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
			f.append(" at("+str(sum([float(root.find("construction").find('element[@label="'+v+'"]').find("coords").attrib["x"]) for n,v in li.find("input").attrib.items()])/len(li.find("input").attrib))+","+str(sum([float(root.find("construction").find('element[@label="'+v+'"]').find("coords").attrib["y"]) for n,v in li.find("input").attrib.items()])/len(li.find("input").attrib))+"){$"+unicode_to_latex(se.attrib["label"])+"$};")
for li in root.find("construction").findall("element[@type='line']"):
	if li.find("show").attrib["object"]=="false":
		continue
	coor=li.find("coords")
	if abs(float(coor.attrib["x"]))>abs(float(coor.attrib["y"])):
		f.append("\n\\draw plot({"+str(-float(coor.attrib["z"])/float(coor.attrib["x"]))+"+("+str(-float(coor.attrib["y"])/float(coor.attrib["x"]))+")*\\x},\\x)")
	else:
		f.append("\n\\draw plot(\\x,{"+str(-float(coor.attrib["z"])/float(coor.attrib["y"]))+"+("+str(-float(coor.attrib["x"])/float(coor.attrib["y"]))+")*\\x})")
	if li.find("show").attrib["label"]=="true":
		f.append("node")
		if len(li.findall("labelOffset")):
			f.append("[xshift="+li.find("labelOffset").attrib["x"]+",yshift="+li.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[right]")
		f.append("{$"+unicode_to_latex(li.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='Segment']"):
	se=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	pt1=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	pt2=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
	if se.find("lineStyle").attrib["type"]=="0":
		dash=""
	else:
		dash="[dash pattern=on 4pt off 4pt]"
	f.append("\n\\draw"+dash+"("+pt1.find("coords").attrib["x"]+","+pt1.find("coords").attrib["y"]+")--("+pt2.find("coords").attrib["x"]+","+pt2.find("coords").attrib["y"]+")")
	if se.find("show").attrib["label"]=="true":
		f.append("node")
		if len(se.findall("labelOffset")):
			f.append("[midway,xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[midway,right]")
		f.append("{$"+unicode_to_latex(se.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='Ray']"):
	se=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	pt1=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	pt2=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
	f.append("\n\\draw("+pt1.find("coords").attrib["x"]+","+pt1.find("coords").attrib["y"]+")--("+str(float(pt2.find("coords").attrib["x"])*3-float(pt1.find("coords").attrib["x"])*2)+","+str(float(pt2.find("coords").attrib["y"])*3-float(pt1.find("coords").attrib["y"])*2)+")")
	if se.find("show").attrib["label"]=="true":
		f.append("node")
		if len(se.findall("labelOffset")):
			f.append("[midway,xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[midway,right]")
		f.append("{$"+unicode_to_latex(se.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='Vector']"):
	se=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	pt1=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	pt2=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
	f.append("\n\\draw[-latex]("+pt1.find("coords").attrib["x"]+","+pt1.find("coords").attrib["y"]+")--("+pt2.find("coords").attrib["x"]+","+pt2.find("coords").attrib["y"]+")")
	if se.find("show").attrib["label"]=="true":
		f.append("node")
		if len(se.findall("labelOffset")):
			f.append("[midway,xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[midway,right]")
		f.append("{$"+unicode_to_latex(se.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='Semicircle']"):
	se=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	pt1=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	pt2=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
	f.append("\n\\draw("+pt1.find("coords").attrib["x"]+","+pt1.find("coords").attrib["y"]+")--("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")arc(0:180:"+str(sqrt((float(pt1.find("coords").attrib["x"])-float(pt2.find("coords").attrib["x"]))**2+(float(pt1.find("coords").attrib["y"])-float(pt2.find("coords").attrib["y"]))**2)/2)+")")
	if se.find("show").attrib["label"]=="true":
		f.append("node")
		if len(se.findall("labelOffset")):
			f.append("[midway,xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[midway,above]")
		f.append("{$"+unicode_to_latex(se.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("expression[@type='function']"):
	se=root.find("construction").find('element[@label="'+li.attrib["label"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	f.append("\n\\draw plot[smooth](\\x,{"+li.attrib["exp"][li.attrib["exp"].index('=')+1:].strip().replace('x','(\\x)')+"})")
	if se.find("show").attrib["label"]=="true":
		f.append("node")
		if len(se.findall("labelOffset")):
			f.append("[xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[right]")
		f.append("{$"+unicode_to_latex(se.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='PolyLine']"):
	se=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	for n, v in li.find("input").attrib.items():
		pt=root.find("construction").find('element[@label="'+v+'"]')
		if n=="a0":
			f.append("\n\\draw("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")")
			continue
		f.append("--("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")")
	f.append(";")
	if se.find("show").attrib["label"]=="true":
		f.append("\\draw node")
		if len(se.findall("labelOffset")):
			f.append("[xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
		f.append(" at("+str(sum([float(root.find("construction").find('element[@label="'+v+'"]').find("coords").attrib["x"]) for n,v in li.find("input").attrib.items()])/len(li.find("input").attrib))+","+str(sum([float(root.find("construction").find('element[@label="'+v+'"]').find("coords").attrib["y"]) for n,v in li.find("input").attrib.items()])/len(li.find("input").attrib))+"){$"+unicode_to_latex(se.attrib["label"])+"$};")
for li in root.find("construction").findall("command[@name='Angle']"):
	se=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	if se.find("show").attrib["object"]=="false":
		continue
	pt1=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
	pt2=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	pt3=root.find("construction").find('element[@label="'+li.find("input").attrib["a2"]+'"]')
	d12=sqrt((float(pt1.find("coords").attrib["x"])-float(pt2.find("coords").attrib["x"]))**2+(float(pt1.find("coords").attrib["y"])-float(pt2.find("coords").attrib["y"]))**2)
	d13=sqrt((float(pt1.find("coords").attrib["x"])-float(pt3.find("coords").attrib["x"]))**2+(float(pt1.find("coords").attrib["y"])-float(pt3.find("coords").attrib["y"]))**2)
	pt12="("+str(float(pt1.find("coords").attrib["x"])+(float(pt2.find("coords").attrib["x"])-float(pt1.find("coords").attrib["x"]))*0.3/d12)+","+str(float(pt1.find("coords").attrib["x"])+(float(pt2.find("coords").attrib["y"])-float(pt1.find("coords").attrib["y"]))*0.3/d12)+")"
	ang2=atan2(float(pt2.find("coords").attrib["y"])-float(pt1.find("coords").attrib["y"]),float(pt2.find("coords").attrib["x"])-float(pt1.find("coords").attrib["x"]))
	ang3=atan2(float(pt3.find("coords").attrib["y"])-float(pt1.find("coords").attrib["y"]),float(pt3.find("coords").attrib["x"])-float(pt1.find("coords").attrib["x"]))
	f.append("\n\\draw[color=black!50!green,very thick,fill=green,fill opacity=0.1]("+pt1.find("coords").attrib["x"]+","+pt1.find("coords").attrib["y"]+")--+("+str(ang2*180/pi)+":0.3)arc("+str(ang2*180/pi)+":"+str(ang3*180/pi)+":0.3)")
	if se.find("show").attrib["label"]=="true":
		f.append("node")
		if len(se.findall("labelOffset")):
			f.append("[xshift="+se.find("labelOffset").attrib["x"]+",yshift="+se.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[above]")
		f.append("{$"+unicode_to_latex(se.attrib["label"])+"$}")
	f.append("--cycle;")
for li in root.find("construction").findall("command[@name='CircleArc']"):
	co=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	ptA=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	ptB=root.find("construction").find('element[@label="'+li.find("input").attrib["a2"]+'"]')
	ptC=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
	angC=atan2(float(ptC.find("coords").attrib["y"])-float(ptA.find("coords").attrib["y"]),float(ptC.find("coords").attrib["x"])-float(ptA.find("coords").attrib["x"]))*180/pi
	angB=atan2(float(ptB.find("coords").attrib["y"])-float(ptA.find("coords").attrib["y"]),float(ptB.find("coords").attrib["x"])-float(ptA.find("coords").attrib["x"]))*180/pi
	if angB<angC:
		angB=angB+360
	f.append("\n\\draw("+ptC.find("coords").attrib["x"]+","+ptC.find("coords").attrib["y"]+")arc("+str(angC)+":"+str(angB)+":"+str(sqrt(-float(co.find("matrix").attrib["A2"])+float(co.find("matrix").attrib["A4"])**2+float(co.find("matrix").attrib["A5"])**2))+")")
	co.set("type","done")
	if co.find("show").attrib["label"]=="true":
		f.append("node")
		if len(co.findall("labelOffset")):
			f.append("[xshift="+co.find("labelOffset").attrib["x"]+",yshift="+co.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[above right]")
		f.append("{$"+unicode_to_latex(co.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='CircleSector']"):
	co=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	ptA=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	ptB=root.find("construction").find('element[@label="'+li.find("input").attrib["a2"]+'"]')
	ptC=root.find("construction").find('element[@label="'+li.find("input").attrib["a1"]+'"]')
	cen="("+str(-float(co.find("matrix").attrib["A4"]))+","+str(-float(co.find("matrix").attrib["A5"]))+")"
	angC=atan2(float(ptC.find("coords").attrib["y"])-float(ptA.find("coords").attrib["y"]),float(ptC.find("coords").attrib["x"])-float(ptA.find("coords").attrib["x"]))*180/pi
	angB=atan2(float(ptB.find("coords").attrib["y"])-float(ptA.find("coords").attrib["y"]),float(ptB.find("coords").attrib["x"])-float(ptA.find("coords").attrib["x"]))*180/pi
	if angB<angC:
		angB=angB+360
	f.append("\n\\draw[color=brown,fill=brown,fill opacity=0.1]"+cen+"--("+ptC.find("coords").attrib["x"]+","+ptC.find("coords").attrib["y"]+")arc("+str(angC)+":"+str(angB)+":"+str(sqrt(-float(co.find("matrix").attrib["A2"])+float(co.find("matrix").attrib["A4"])**2+float(co.find("matrix").attrib["A5"])**2))+")--"+cen)
	co.set("type","done")
	if co.find("show").attrib["label"]=="true":
		f.append("node")
		if len(co.findall("labelOffset")):
			f.append("[xshift="+co.find("labelOffset").attrib["x"]+",yshift="+co.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[above right]")
		f.append("{$"+unicode_to_latex(co.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='CircumcircleArc']"):
	co=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	ptB=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	ptC=root.find("construction").find('element[@label="'+li.find("input").attrib["a2"]+'"]')
	angC=atan2(float(ptC.find("coords").attrib["y"])+float(co.find("matrix").attrib["A5"]),float(ptC.find("coords").attrib["x"])+float(co.find("matrix").attrib["A4"]))*180/pi
	angB=atan2(float(ptB.find("coords").attrib["y"])+float(co.find("matrix").attrib["A5"]),float(ptB.find("coords").attrib["x"])+float(co.find("matrix").attrib["A4"]))*180/pi
	if angB<angC:
		angB=angB+360
	f.append("\n\\draw("+ptC.find("coords").attrib["x"]+","+ptC.find("coords").attrib["y"]+")arc("+str(angC)+":"+str(angB)+":"+str(sqrt(-float(co.find("matrix").attrib["A2"])+float(co.find("matrix").attrib["A4"])**2+float(co.find("matrix").attrib["A5"])**2))+")")
	co.set("type","done")
	if co.find("show").attrib["label"]=="true":
		f.append("node")
		if len(co.findall("labelOffset")):
			f.append("[xshift="+co.find("labelOffset").attrib["x"]+",yshift="+co.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[above right]")
		f.append("{$"+unicode_to_latex(co.attrib["label"])+"$}")
	f.append(";")
for li in root.find("construction").findall("command[@name='CircumcircleSector']"):
	co=root.find("construction").find('element[@label="'+li.find("output").attrib["a0"]+'"]')
	ptB=root.find("construction").find('element[@label="'+li.find("input").attrib["a0"]+'"]')
	ptC=root.find("construction").find('element[@label="'+li.find("input").attrib["a2"]+'"]')
	cen="("+str(-float(co.find("matrix").attrib["A4"]))+","+str(-float(co.find("matrix").attrib["A5"]))+")"
	angC=atan2(float(ptC.find("coords").attrib["y"])+float(co.find("matrix").attrib["A5"]),float(ptC.find("coords").attrib["x"])+float(co.find("matrix").attrib["A4"]))*180/pi
	angB=atan2(float(ptB.find("coords").attrib["y"])+float(co.find("matrix").attrib["A5"]),float(ptB.find("coords").attrib["x"])+float(co.find("matrix").attrib["A4"]))*180/pi
	if angB<angC:
		angB=angB+360
	f.append("\n\\draw[color=brown,fill=brown,fill opacity=0.1]"+cen+"--("+ptC.find("coords").attrib["x"]+","+ptC.find("coords").attrib["y"]+")arc("+str(angC)+":"+str(angB)+":"+str(sqrt(-float(co.find("matrix").attrib["A2"])+float(co.find("matrix").attrib["A4"])**2+float(co.find("matrix").attrib["A5"])**2))+")--"+cen)
	co.set("type","done")
	if co.find("show").attrib["label"]=="true":
		f.append("node")
		if len(co.findall("labelOffset")):
			f.append("[xshift="+co.find("labelOffset").attrib["x"]+",yshift="+co.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[above right]")
		f.append("{$"+unicode_to_latex(co.attrib["label"])+"$}")
	f.append(";")
for co in root.find("construction").findall("element[@type='conic']"):
	if co.find("show").attrib["object"]=="false":
		continue
	m=co.find("matrix")
	if m.attrib["A0"]=="1.0" and m.attrib["A1"]=="1.0" and m.attrib["A3"]=="0.0":
		f.append("\n\\draw("+str(-float(m.attrib["A4"]))+","+str(-float(m.attrib["A5"]))+")circle("+str(sqrt(-float(m.attrib["A2"])+float(m.attrib["A4"])**2+float(m.attrib["A5"])**2))+");")
		continue
	e=co.find("eigenvectors")
	x0=float(e.attrib["x0"])
	y0=float(e.attrib["y0"])
	x1=float(e.attrib["x1"])
	y1=float(e.attrib["y1"])
	if x0*y1<x1*y0:
		x1=float(e.attrib["x0"])
		y1=float(e.attrib["y0"])
		x0=float(e.attrib["x1"])
		y0=float(e.attrib["y1"])
	def matrix_multiply(A, B):
		return [[sum(a*b for a, b in zip(A_row, B_col)) for B_col in zip(*B)] for A_row in A]

	A = [[x0,y0,0],[x1,y1,0],[0,0,1]]
	B = [[float(m.attrib["A0"]),float(m.attrib["A3"]),float(m.attrib["A4"])],[float(m.attrib["A3"]),float(m.attrib["A1"]),float(m.attrib["A5"])],[float(m.attrib["A4"]),float(m.attrib["A5"]),float(m.attrib["A2"])]]
	C = [[x0,x1,0],[y0,y1,0],[0,0,1]]

	s = matrix_multiply(A, matrix_multiply(B, C))
	if abs(s[0][0])<0.0001*abs(s[1][1]):
		f.append("\n\\draw[rotate="+str(atan2(y0,x0)/pi*180)+"]plot[smooth]({"+str(-s[1][1]/2/s[0][2])+"*(\\x)^2+("+str(-s[1][2]/s[0][2])+")*\\x+("+str(-s[2][2]/2/s[0][2])+")},\\x)")
	elif abs(s[1][1])<0.0001*abs(s[0][0]):
		f.append("\n\\draw[rotate="+str(atan2(y0,x0)/pi*180)+"]plot[smooth](\\x,{"+str(-s[0][0]/2/s[1][2])+"*(\\x)^2+("+str(-s[0][2]/s[1][2])+")*\\x+("+str(-s[2][2]/2/s[1][2])+")})")
	else:
		alpha = -s[0][2] / s[0][0]
		beta = -s[1][2] / s[1][1]
		t = alpha * s[0][2] + beta * s[1][2] + s[2][2]
		if s[0][0]*s[1][1]>0:
			f.append("\n\\draw[rotate="+str(atan2(y0,x0)/pi*180)+"]("+str(alpha)+","+str(beta)+")ellipse("+str(sqrt(-t/s[0][0]))+" and "+str(sqrt(-t/s[1][1]))+")")
		elif t*s[0][0]<0:
			f.append("\n\\draw[rotate="+str(atan2(y0,x0)/pi*180)+"]plot[smooth,variable=\\t,domain=-80:80]({"+str(sqrt(-t/s[0][0]))+"*sec(\\t)+("+str(alpha)+")},{"+str(sqrt(t/s[1][1]))+"*tan(\\t)+("+str(beta)+")});\n\\draw plot[rotate="+str(atan2(y0,x0)/pi*180)+",variable=\\t,domain=100:260]({"+str(sqrt(-t/s[0][0]))+"*sec(\\t)+("+str(alpha)+")},{"+str(sqrt(t/s[1][1]))+"*tan(\\t)+("+str(beta)+")})")
		else:
			f.append("\n\\draw[rotate="+str(atan2(y0,x0)/pi*180)+"]plot[smooth,variable=\\t,domain=-80:80]({"+str(sqrt(t/s[0][0]))+"*tan(\\t)+("+str(alpha)+")},{"+str(sqrt(-t/s[1][1]))+"*sec(\\t)+("+str(beta)+")});\n\\draw plot[rotate="+str(atan2(y0,x0)/pi*180)+",variable=\\t,domain=100:260]({"+str(sqrt(t/s[0][0]))+"*tan(\\t)+("+str(alpha)+")},{"+str(sqrt(-t/s[1][1]))+"*sec(\\t)+("+str(beta)+")})")
	if co.find("show").attrib["label"]=="true":
		f.append("node")
		if len(co.findall("labelOffset")):
			f.append("[xshift="+co.find("labelOffset").attrib["x"]+",yshift="+co.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[above right]")
		f.append("{$"+unicode_to_latex(co.attrib["label"])+"$}")
	f.append(";")
for pt in root.find("construction").findall("element[@type='point']"):
	if pt.find("show").attrib["object"]=="false" or  pt.find("coords").attrib["x"]=='NaN' or  pt.find("coords").attrib["y"]=='NaN':
		continue
	f.append("\n\\draw[fill=blue]("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")circle(\\pointsize);")
	f.append("\n\\draw[blue]("+pt.find("coords").attrib["x"]+","+pt.find("coords").attrib["y"]+")")
	if pt.find("show").attrib["label"]=="true":
		f.append("node")
		if len(pt.findall("labelOffset")):
			f.append("[xshift="+pt.find("labelOffset").attrib["x"]+",yshift="+pt.find("labelOffset").attrib["y"]+"]")
		else:
			f.append("[above right]")
		f.append("{$"+unicode_to_latex(pt.attrib["label"])+"$}")
	f.append(";")
f.append("\n\\end{tikzpicture}\n\\end{document}")
temp_dir.cleanup()
print(''.join(f))
