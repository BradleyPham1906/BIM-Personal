import zipfile,re,sys
z=zipfile.ZipFile(sys.argv[1])
t=z.read('ifcopenshell/util/schema/Pset_IFC4X3.ifc').decode(errors='ignore')
ents={}
for m in re.finditer(r"^#(\d+)=\s*(\w+)\((.*)\);\s*$",t,re.M):
    ents[m.group(1)]=(m.group(2),m.group(3))
want=['Pset_WallCommon','Qto_WallBaseQuantities','Pset_SlabCommon','Qto_SlabBaseQuantities','Pset_ColumnCommon','Qto_ColumnBaseQuantities','Pset_DoorCommon','Pset_WindowCommon','Qto_DoorBaseQuantities','Pset_BeamCommon','Pset_SpaceCommon','Qto_SpaceBaseQuantities']
for k,(c,a) in ents.items():
    if c=='IFCPROPERTYSETTEMPLATE':
        nm=re.search(r"'(Pset_\w+|Qto_\w+)'",a)
        if nm and nm.group(1) in want:
            refs=re.findall(r'#(\d+)',a.split('(#',1)[1] if '(#' in a else '')
            names=[]
            for r in refs:
                if r in ents and ents[r][0]=='IFCSIMPLEPROPERTYTEMPLATE':
                    names.append(re.findall(r"'([^']*)'",ents[r][1])[1])
            app=re.findall(r"'([^']*)'",a)
            print(nm.group(1),'| applies:',app[3] if len(app)>3 else '?','|',', '.join(names))
