import pyvista as pv
from vpython import *
from ChemFun import *
import wx
import re as re
import numpy as np

app    = wx.App()
frame  = wx.Frame(None, title='PyAtomSTL',size = (560,520))
panel  = wx.Panel(frame)
Labels = []
minX = minY = minZ = 0.0

scene   = canvas(background = color.black,width=800,height=800)
plotter = pv.Plotter()

Vi = False

REG1 = '^(\d+),(\d+)\s-\s(\d*\.?\d*)\s*([DT]*)$'
REG2 = r'^([a-zA-Z]+)'+3*r'\s+(\-?\d*\.?\d*e?\-?\d*)'+r'\s*$'
REG3 = '^(\d*\.?\d*)\s*-\s*(\d*\.?\d*)\s*([DT]*)$'
REG4 = r'^(\d+)\s*$'
REG5 = r'^'+3*'(\-?\d*\.?\d*e?\-?\d*)\s+'+'([A-Z][a-z]*)'
REG6 = r'^(\d+)\s+(\d+)\s+(\d+)'

def LeeSTL(T):
    file = list(open(T))
    ver  = []
    v    = []
    for t in file:
        v.append([float(r) for r in t.split(',')])
        if len(v)==3:
            ver.append(v)
            v = []
    return ver

class Atomo():
    def __init__(self,ind,sym,pos):
        (R, G, B) = GetColor(sym)
        self.indice   = (str(ind)).zfill(3)
        self.simbolo  = sym
        self.posicion = vec(pos[0],pos[1],pos[2])
        self.posicionVis = np.array([float(k) for k in pos])
        self.colorVis    = (R,G,B)
        self.color    = vec(R,G,B)/255
        self.radio    = GetRadius(sym)/2

Ejes = compound([cylinder(pos = vec(0,0,0),axis = vec(3,0,0), color = color.red, radius = 0.10),
        cylinder(pos = vec(0,0,0), axis = vec(0,3,0),   color = color.green,  radius = 0.10),
        cylinder(pos = vec(0,0,0), axis = vec(0,0,3),   color = vec(0.2,1,1), radius = 0.10),
        cone(pos = vec(3,0,0),     axis = vec(0.8,0,0), color = color.red,    radius = 0.2),
        cone(pos = vec(0,3,0),     axis = vec(0,0.8,0), color = color.green,  radius = 0.2),
        cone(pos = vec(0,0,3),     axis = vec(0,0,0.8), color = vec(0.2,1,1), radius = 0.2)])

def Borrar(x):
    Ne.Clear()
    DibujaEnlaces(0)

def vista(x):
    scene.fov = radians(60) if Vista.Value else radians(3)
    
def NuevoEnlace(x):
    if T1.Value!=T2.Value and str(T1.Value).isdigit() and str(T2.Value).isdigit():
        t = str(T1.Value).zfill(3)+','+str(T2.Value).zfill(3)
        t1 = set([str(T1.Value).zfill(3),str(T2.Value).zfill(3)])
        
        k1 = [set((h.split(' - ')[0]).split(',')) for h in En.GetStrings()]
        k2 = [set((h.split(' - ')[0]).split(',')) for h in Ne.GetStrings()]
        if (t1 in k1) or (t1 in k2):
            dlg = wx.MessageDialog(panel,'Ese enlace ya está en el sistema.','PyAtomSTL',wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            t = t +' - 0.10'
            Ne.Append(t)
            Ne.SetCheckedStrings([t])
            DibujaEnlaces(0)

def DibujaEnlaces(x):
    for n in scene.objects:
        if isinstance(n, cylinder):
            n.visible = False
    for n in [En.GetCheckedStrings(),Ne.GetCheckedStrings()]:
        for z1 in n:
            [e0,e1,r,d] = [f(x) for f,x in zip([int,int,float,str],[re.search(REG1,z1).group(h) for h in range(1,5)])]
            r  = float(r)
            p   = (Atomos[e1].posicion-Atomos[e0].posicion)
            per = norm(vec(p.z,0,-p.x))
            if d == 'D':
                cylinder(radius = r, pos = Atomos[e0].posicion + per*1.2*r, axis = p,color = vec(0.8,0.8,0.8))
                cylinder(radius = r, pos = Atomos[e0].posicion - per*1.2*r, axis = p,color = vec(0.8,0.8,0.8))
            elif d == 'T':
                cylinder(radius = r, pos = Atomos[e0].posicion + per*3*r, axis = p,color = vec(0.8,0.8,0.8))
                cylinder(radius = r, pos = Atomos[e0].posicion - per*3*r, axis = p,color = vec(0.8,0.8,0.8))
                cylinder(radius = r, pos = Atomos[e0].posicion, axis = p, color = vec(0.8,0.8,0.8))
            else:
                cylinder(radius = r, pos = Atomos[e0].posicion, axis = p, color = vec(0.8,0.8,0.8))

def ActualizaPAS():
    global Atomos
    for n in scene.objects:
            if not isinstance(n, compound):
                n.visible = False
    Esferas = [sphere(pos = A.posicion, radius = A.radio, color = A.color) for A in Atomos]
    Labels  = [label(pos =  A.posicion, text = A.simbolo + '\n' + A.indice, box = False,opacity = 0.0, visible = M.GetValue()) for A in Atomos]
    DibujaEnlaces(0)

def Repetidos():
    k1 = [set((h.split(' - ')[0]).split(',')) for h in En.GetStrings()]
    k2 = [set((h.split(' - ')[0]).split(',')) for h in Ne.GetStrings()]
    R  = [i for i,h2 in enumerate(k2) if h2 in k1]
    R.sort(reverse = True)
    return R

def RenderVista():
    global Atomos
    E = [pv.Sphere(center = a.posicionVis, radius = a.radio) for a in Atomos]
    Esferas = [plotter.add_mesh(e, color = a.colorVis) for e, a in zip(E, Atomos)]
    
    

def Actualiza(SD,Dis,rad_en):
    global Labels,CM,muestra,DT,Atomos
    if muestra:
        for n in scene.objects:
            if not isinstance(n, compound):
                n.visible = False
        
        Esferas = [sphere(pos = A.posicion, radius = A.radio, color = A.color) for A in Atomos]
        Labels  = [label(pos = A.posicion, text = A.simbolo + '\n' + A.indice, box = False,opacity = 0.0, visible = M.GetValue()) for A in Atomos]
    Z = []
    for sd,r,D in zip(SD,rad_en,Dis):
        Enlaces = []
        for i in Atomos:
            for j in Atomos:
                if abs(mag(i.posicion-j.posicion)-D) < D/100:
                    Enlaces.append(frozenset([i.indice,j.indice]))
        Enlaces = [list(e) for e in list(set(Enlaces))]
        for e in Enlaces:
            Z.append(str(e[0])+','+str(e[1])+' - '+str(r) + sd)
            
    Z.sort()
    En.Clear()
    En.Append(Z)
    En.SetCheckedItems(range(len(Z)))

    for r in Repetidos(): Ne.Delete(r)
    
    if muestra:
        DibujaEnlaces(0)
        CM = vec(0,0,0)
        for a in Atomos:
            CM = CM + a.posicion
        CM = CM / len(Atomos)
    RenderVista()

def setorigen(x):
    global CM
    scene.center = vec(0,0,0) if R1.GetValue() else CM
    
def seccion(x):
    Z = K.GetCheckedStrings()
    K0 = [re.search(REG3,k).group(3) for k in Z]
    K1 = [float(re.search(REG3,k).group(1)) for k in Z]
    K2 = [float(re.search(REG3,k).group(2)) for k in Z]
    Actualiza(K0,K1,K2)
    
def act_etiquetas(x):
    global Labels
    for L in Labels:
        L.visible = M.GetValue()

def act_ejes(x):
    Ejes.visible = Ej.GetValue()

def Inicia(name):
    global DisStr,Atomos,muestra
    muestra = 0; LA = []
    A = [a.strip() for a in list(open(name,'r'))]
    for a in A:
        if re.search(REG4,a):
            res = re.search(REG4,a)
            N = int(res.group(1))
        if re.search(REG2,a):
            res = re.search(REG2,a)
            LA.append([res.group(1),[float(res.group(2)),float(res.group(3)),float(res.group(4))]])
    Atomos = [Atomo(i,a[0],a[1]) for i,a in enumerate(LA)]

    Distancias = []
    for i in Atomos:
        disT = []
        for j in Atomos:
            if i.indice != j.indice:
                disT.append(round(mag(i.posicion-j.posicion),3))
        disT.sort(); mk = disT[0]
        disT = [k for k in disT if k<=1.5*mk]
        Distancias.extend(disT)
    Distancias = list(set(Distancias))
    Distancias.sort()
    DisStr = [str(t)+' - 0.10' for t in Distancias]

def IniciaMOL(name):
    global DisStr,Atomos,muestra
    muestra = 0; LA = []; Emol=[]
    A = [a.strip() for a in list(open(name,'r'))]
    for a in A:
        if re.search(REG5,a):
            res = re.search(REG5,a)
            LA.append([res.group(4),vec(float(res.group(1)),float(res.group(2)),float(res.group(3)))])
        if re.search(REG6,a) and len(LA)!= 0:
            res = re.search(REG6,a)
            e1 = str(int(res.group(1))-1)
            e2 = str(int(res.group(2))-1)
            Emol.append(e1.zfill(3) + ',' + e2.zfill(3) +' - 0.1 '+['','','D','T'][int(res.group(3))])
    Atomos = [Atomo(i,a[0],a[1]) for i,a in enumerate(LA)]
    Distancias = []
    for i in Atomos:
        disT = []
        for j in Atomos:
            if i.indice != j.indice:
                disT.append(round(mag(i.posicion-j.posicion),3))
        disT.sort(); mk = disT[0]
        disT = [k for k in disT if k<=1.5*mk]
        Distancias.extend(disT)
    Distancias = list(set(Distancias))
    Distancias.sort()
    DisStr = [str(t)+' - 0.10' for t in Distancias]
    return Emol

def Depura():
    global muestra
    R = []; Repetidos = []; K1 = K.GetItems()
    for i,k in enumerate(K1):
        K.SetCheckedItems([i])
        seccion(1)
        E1 = En.GetItems()
        ya = 0
        for r in R:
            if E1[0] in r:
                Repetidos.append(i)
                ya = 1;break
        if ya == 0: R.append(E1)
    K.Clear()
    for i,k in enumerate(K1):
        if i not in Repetidos: K.Append(k)
    muestra = 1

def esfera(x,y,z,r1): 
    r = 2*r1/100
    V = []
    for v in VE:
        V1 = []
        for v1 in v:
            V1.append([v1[0]*r+x,v1[1]*r+y,v1[2]*r+z-r1])
        V.append(V1)
    return V

def cilindro(x1,y1,z1,x2,y2,z2,r,dt):
    r = 2*r/10
    rp2 = vec(x1,y1,z1) 
    rp1 = vec(x2,y2,z2) 
    rp = rp2-rp1; C1 = vec(0,1,0)
    L = mag(rp)/100
    P = cross(C1,rp)
    t = diff_angle(rp,C1)
    V = []
    for v in [VC,VC2,VC3][{'':0,'D':1,'T':2}[dt]]:
        V1 = []
        for v1 in v:
            C = vec(v1[0]*r,v1[1]*r,v1[2]*L)
            C = rotate(C,angle = pi/2,axis = vec(1,0,0))
            C = rp2+rotate(C,angle = t,axis = P)
            V1.append([C.x,C.y,C.z])
        V.append(V1)
    return V

def Graba(V):
    global salida, minX,minY,minZ
    for v in V:
        salida.write('facet normal 0.0 0.0 0.0\n')
        salida.write('outer loop\n')
        for x in v:
            j = [str(n) for n in x]
            salida.write('vertex ' + ' '.join(j)+'\n')
            if float(j[0])<minX: minX = float(j[0])
            if float(j[1])<minY: minY = float(j[1])
            if float(j[2])<minZ: minZ = float(j[2])
        salida.write('endloop\n')
        salida.write('endfacet\n')
        
def STL(nam):
    global salida, minX,minY,minZ
    salida = open(nam,'w')
    salida.write('solid R_Espejel\n')
    for a in Atomos:
        E = esfera(a.posicion.x,a.posicion.y,a.posicion.z,a.radio)
        Graba(E)
    for EN in [En.GetCheckedStrings(),Ne.GetCheckedStrings()]:
        for k1 in EN:
            [e0,e1,r,d] = [f(x) for f,x in zip([int,int,float,str],[re.search(REG1,k1).group(h) for h in range(1,5)])]
            x1,y1,z1 = Atomos[e0].posicion.x,Atomos[e0].posicion.y,Atomos[e0].posicion.z
            x2,y2,z2 = Atomos[e1].posicion.x,Atomos[e1].posicion.y,Atomos[e1].posicion.z
            Graba(cilindro(x1,y1,z1,x2,y2,z2,r,d))
    salida.write('endsolid R_Espejel\n')
    salida.close()
    #print(minX,minY,minZ)

def CRadio(x):
    k = At.GetString(At.GetSelection())
    k = k.split(' - ')
    Ar.Value = k[1]

def CRadioE(x):
    B_id = x.GetEventObject().GetName()
    k    = DicFun1[B_id].GetString(DicFun1[B_id].GetSelection()).replace(' D','')
    k    = k.replace(' T','')
    k    = k.split(' - ')
    DicTxt1[B_id].Value = k[1]

def ActTodosEn(dummy):
    re = RE.Value.strip()
    
    seK = K.GetCheckedItems()
    K1  = [k.split(' - ')[0]+' - '+re for k in K.GetItems()]
    K.SetItems(K1)
    K.SetCheckedItems(seK)

    seK = En.GetCheckedItems()
    K1 = [k.split(' - ')[0]+' - '+re for k in En.GetItems()]
    En.SetItems(K1)
    En.SetCheckedItems(seK)

    seK = Ne.GetCheckedItems()
    K1  = [k.split(' - ')[0]+' - '+re for k in Ne.GetItems()]
    Ne.SetItems(K1)
    Ne.SetCheckedItems(seK)
    
    DibujaEnlaces(0)

def CambiarRadio(x):
    try:
        k = At.GetString(At.GetSelection())
        k = k.split(' - ')
        At.SetString(At.GetSelection(),k[0]+' - '+str(float(Ar.Value)))
        for a in Atomos:
            if a.simbolo==k[0]: a.radio = float(Ar.Value)
        seccion(0)
    except:
        dlg = wx.MessageDialog(panel,'Debes resaltar una entrada de la lista\ny dar un radio válido','PyAtomSTL',wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def CambiarRadioE(x):
    try:
        B_id = x.GetEventObject().GetName()
        h = DicFun1[B_id].GetString(DicFun1[B_id].GetSelection())
        dt = (h.strip())[-1] if ('D' in h or 'T' in h) else ''
        k = h.split(' - ')
        DicFun1[B_id].SetString(DicFun1[B_id].GetSelection(),k[0]+' - '+str(float(DicTxt1[B_id].Value))+ ' ' + dt) 
        if B_id == 'CR1': seccion(0)
        DibujaEnlaces(0)
    except:
        dlg = wx.MessageDialog(panel,'Debes resaltar una entrada de la lista!', 'PyAtomSTL',wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def DSE(x):
    try:
        B_id = x.GetEventObject().GetName()
        k = DicFun1[B_id].GetString(DicFun1[B_id].GetSelection())
        if 'D' in k:
            DicFun1[B_id].SetString(DicFun1[B_id].GetSelection(),k.replace('D','T'))
        elif 'T' in k:
            DicFun1[B_id].SetString(DicFun1[B_id].GetSelection(),k.replace('T',''))
        else:
            DicFun1[B_id].SetString(DicFun1[B_id].GetSelection(),k + ' D')
        if B_id == 'CR1': seccion(0)
        DibujaEnlaces(0)
    except:
        dlg = wx.MessageDialog(panel,'Debes resaltar una entrada de la lista!','PyAtomSTL',wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def STLG(event):
    global ruta
    nam = re.search(r'(^[A-Z]:)*(\\.+)*\\(.+)\..+',ruta).group(3)
    fileDialog = wx.FileDialog(panel,"Exportar archivo STL", wildcard="Archivo STL (*.stl)|*.stl",
                               style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    fileDialog.SetFilename(nam)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ruta = fileDialog.GetPath()
    STL(ruta)

def XYZR(event):
    global DisStr,ruta
    fileDialog = wx.FileDialog(panel,"Leer archivo XYZ", wildcard="Archivo XYZ (*.xyz)|*.xyz",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    RE.value = '0.10'
    ruta = fileDialog.GetPath()
    Inicia(ruta)
    K.SetItems(DisStr)
    En.SetItems([])
    Ne.SetItems([])
    Depura()
    K.SetCheckedItems([0])
    ListaRadios()
    seccion(1)
    
def MOLR(event):
    global DisStr,ruta
    fileDialog = wx.FileDialog(panel,"Leer archivo MOL", wildcard="Archivo MOL (*.mol)|*.mol",
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    RE.value = '0.10'
    ruta = fileDialog.GetPath()
    Emol = IniciaMOL(ruta)
    K.SetItems(DisStr)
    En.SetItems([])
    Depura()
    Ne.SetItems(Emol)
    Ne.SetCheckedItems(range(len(Ne.GetStrings())))
    ListaRadios()
    seccion(1)

def ListaRadios():
    AtS = []; At.SetItems([])
    for a in Atomos:
        if a.simbolo not in AtS:
            At.Append(a.simbolo+' - '+str(a.radio))
            AtS.append(a.simbolo)

def Originales(x):
    for a in Atomos: a.radio = Radios[a.simbolo]
    ListaRadios()
    seccion(0)

def LeerPAS(x):
    global ruta,muestra,Atomos
    fileDialog = wx.FileDialog(panel,"Leer archivo PAS", wildcard='Archivo PAS (*.pas)|*.pas',
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ruta = fileDialog.GetPath()
    K.Clear(); En.Clear(); Ne.Clear(); At.Clear()
    Atomos = []; 
    archivo = list(open(ruta,'r'))
    for a in archivo:
        k = a.split(',')
        if k[0] == '@1':
            res = re.search(r'<(\-?\d*\.?\d*e?\-?\d*),\s?(\-?\d*\.?\d*e?\-?\d*),\s?(\-?\d*\.?\d*e?\-?\d*)',a)
            r1,r2,r3 = float(res.group(1)),float(res.group(2)),float(res.group(3))
            Atomos.append(Atomo(int(k[1]),k[2],vec(r1,r2,r3)))
        if k[0] == '@2':
            At.Append(k[1]+' - '+k[2])
            for a in Atomos:
                if a.simbolo == k[1]: a.radio = float(k[2])
        if k[0] == '@3':
            K.Append(k[1]+' - '+k[2]+k[3])
        if k[0] == '@4':
            res = re.search(r'\((.*)\)',k[1])
            K.SetCheckedItems([int(h) for h in res.group(1).split()])
        if k[0] == '@5':
            En.Append(k[1].zfill(3)+','+k[2].zfill(3)+' - '+k[3]+' '+k[4])
        if k[0] == '@6':
            res = re.search(r'\((.*)\)',k[1])
            En.SetCheckedItems([int(h) for h in res.group(1).split()])
        if k[0] == '@7':
            Ne.Append(k[1].zfill(3)+','+k[2].zfill(3)+' - '+k[3]+' '+k[4])
        if k[0] == '@8':
            res = re.search(r'\((.*)\)',k[1])
            Ne.SetCheckedItems([int(h) for h in res.group(1).split()])
    ActualizaPAS()
    K.Enabled = True

def SalvarPAS(x):
    global ruta
    nam = re.search(r'(^[A-Z]:)*(\\.+)*\\(.+)\..+',ruta).group(3)
    fileDialog = wx.FileDialog(panel,"Salvar archivo PAS", wildcard="Archivo PAS (*.pas)|*.pas",
                       style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    fileDialog.SetFilename(nam)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ruta = fileDialog.GetPath()
    salva = open(ruta,'w')
    for a in Atomos:
        salva.write('@1,'+a.indice+','+a.simbolo+','+str(a.posicion)+'\n')
    for a in At.GetItems():
        k = a.split(' - '); salva.write('@2,'+k[0]+','+k[1].strip()+'\n')
    for a in K.GetItems():
        dt = (a.strip())[-1] if ('D' in a or 'T' in a) else ''
        k = a.split(' - '); salva.write('@3,'+k[0]+','+k[1].strip()+','+dt+'\n')
    salva.write('@4,'+str(K.GetCheckedItems()).replace(',','')+'\n')
    for a in En.GetItems():
        dt = (a.strip())[-1] if ('D' in a or 'T' in a) else ''
        a = a.replace('D',''); a = a.replace('T','')
        k = a.split(' - ')
        salva.write('@5,'+k[0]+','+k[1]+','+dt+'\n')
    salva.write('@6,'+str(En.GetCheckedItems()).replace(',','')+'\n')
    for a in Ne.GetItems():
        dt = (a.strip())[-1] if ('D' in a or 'T' in a) else ''
        a = a.replace('D',''); a = a.replace('T','')
        k = a.split(' - ')
        salva.write('@7,'+k[0]+','+k[1].strip()+','+dt+'\n')
    salva.write('@8,'+str(Ne.GetCheckedItems()).replace(',','')+'\n')
    salva.close()

def SelTodos(x):
    B_id = x.GetEventObject().GetName()
    DicFun1[B_id].SetCheckedItems(range(len(DicFun1[B_id].GetItems())) if DicTxt[B_id].GetValue() else [])
    if B_id == 'CR1':
        seccion(0)
    else:
        DibujaEnlaces(0)

def SPNG(x):
    global ruta
    nam = re.search(r'(^[A-Z]:)*(\\.+)*\\(.+)\..+',ruta).group(3)
    scene.capture(nam)
   
ruta = r'\CuCl.xyz'
Inicia('CuCl.xyz')

y1 = 5; y2 = 20; y3 = 20

Vista = wx.CheckBox(panel,pos=(5,15+y1),label = 'Perspectiva')
Vista.Bind(wx.EVT_CHECKBOX,vista)
Vista.SetValue(True)

M = wx.CheckBox(panel,pos=(320,15+y1),label = 'Etiquetas')
M.Bind(wx.EVT_CHECKBOX,act_etiquetas)
M.SetValue(True)

Ej = wx.CheckBox(panel,pos=(410,15+y1),label = 'Ejes')
Ej.Bind(wx.EVT_CHECKBOX,act_ejes)
Ej.SetValue(True)

K1 = wx.StaticBox(panel,pos = (90,0+y1),label='Rotar Sobre:',size=(190,36))
R1 = wx.RadioButton(panel,pos = (100,15+y1),label = '<0,0,0>')
R2 = wx.RadioButton(panel,pos = (180,15+y1),label = 'Centro Geom')
R1.Bind(wx.EVT_RADIOBUTTON,setorigen)
R2.Bind(wx.EVT_RADIOBUTTON,setorigen)
R1.SetValue(True)

St1 = wx.CheckBox(panel,pos=(5,70+y1),   label = '', name = 'CR1')
St2 = wx.CheckBox(panel,pos=(150,70+y1), label = '', name = 'CR2')
St3 = wx.CheckBox(panel,pos=(295,70+y1), label = '', name = 'CR3')

[j.Bind(wx.EVT_CHECKBOX,SelTodos) for j in [St1,St2,St3]]

K = wx.CheckListBox(panel, pos=(5,70+y2), size=(123,120), choices = DisStr, style=0, name = 'CR1')
K.Bind(wx.EVT_CHECKLISTBOX, seccion)
K.Bind(wx.EVT_LISTBOX, CRadioE)

En = wx.CheckListBox(panel, pos=(150,70+y2), size=(130,120), choices =[], style=0, name = 'CR2')
En.Bind(wx.EVT_CHECKLISTBOX, DibujaEnlaces)
En.Bind(wx.EVT_LISTBOX, CRadioE)

Ne = wx.CheckListBox(panel, pos=(295,70+y2), size=(130,120), choices=[], style=0, name = 'CR3')
Ne.Bind(wx.EVT_CHECKLISTBOX, DibujaEnlaces)
Ne.Bind(wx.EVT_LISTBOX, CRadioE)

boton = wx.Button(panel, label='Agregar enlace\nentre átomos:', pos=(430,70+y2),size=(95,35))
boton.Bind(wx.EVT_BUTTON,NuevoEnlace)

T1 = wx.TextCtrl(panel,pos=(430,110+y2),size=(44,18))
T2 = wx.TextCtrl(panel,pos=(480,110+y2),size=(44,18))

boton1 = wx.Button(panel, label='Borrar Lista', pos=(430,166+y2),size=(87,24))
boton1.Bind(wx.EVT_BUTTON,Borrar)

RadEnT1 = wx.TextCtrl(panel,pos = (5,192+y2), size = (40,22),value = '0.10',style = wx.TE_PROCESS_ENTER)
RadEnB1 = wx.Button(panel,pos = (45,190+y2), size = (85,25), label = 'Cambiar radio', name = 'CR1')
RadEnB1.SetToolTip('Cambia el radio de todos los enlaces con la longitud seleccionada')

RadEnT2 = wx.TextCtrl(panel,pos = (150,192+y2), size = (40,22),value = '0.10',style = wx.TE_PROCESS_ENTER)
RadEnB2 = wx.Button(panel,pos = (190,190+y2), size = (92,25), label = 'Cambiar radio', name = 'CR2')
RadEnB2.SetToolTip('Cambia el radio del enlace seleccionado')

RadEnT3 = wx.TextCtrl(panel,pos = (295,192+y2), size = (40,22),value = '0.10',style = wx.TE_PROCESS_ENTER)
RadEnB3 = wx.Button(panel,pos = (335,190+y2), size = (92,25), label = 'Cambiar radio', name = 'CR3')
RadEnB3.SetToolTip('Cambia el radio del enlace seleccionado')

[x.Bind(wx.EVT_BUTTON,CambiarRadioE) for x in [RadEnB1,RadEnB2,RadEnB3]]

BTD1 = wx.Button(panel,pos = (5,220+y2), size = (85,25),   label = 'Enlace S/D/T', name = 'CR1')
BTD2 = wx.Button(panel,pos = (150,220+y2), size = (85,25), label = 'Enlace S/D/T', name = 'CR2')
BTD3 = wx.Button(panel,pos = (295,220+y2), size = (85,25), label = 'Enlace S/D/T', name = 'CR3')

[x.Bind(wx.EVT_BUTTON,DSE) for x in [BTD1,BTD2,BTD3]]
[x.SetToolTip('Enlace sencillo/doble/triple') for x in [BTD1,BTD2,BTD3]]

L2 = wx.StaticText(panel, pos = (5,40+y2),   label = 'Long. enlace - Radio')
L3 = wx.StaticText(panel, pos = (150,40+y2), label = 'Enlace: At1, At2 - Radio')
L4 = wx.StaticText(panel, pos = (295,40+y2), label = 'Enlace: At1, At2 - Radio')

At = wx.ListBox(panel, pos=(5,290+y3), size=(80,120), choices=[], style=0)
At.Bind(wx.EVT_LISTBOX, CRadio)

Ar = wx.TextCtrl(panel,pos = (90,290+y3), size = (40,20),value = '',style = wx.TE_PROCESS_ENTER)
Ar.Bind(wx.EVT_TEXT_ENTER,CambiarRadio)

wx.StaticLine(panel, pos = (5,260+y3), size = (530,2), style = wx.LI_HORIZONTAL)

L1 = wx.StaticText(panel, pos = (5,270+y3),label = 'Átomo - Radio')

boton2 = wx.Button(panel, label='Cambiar radio\ndel átomo', pos=(135,290+y3),size=(100,35))
boton2.Bind(wx.EVT_BUTTON,CambiarRadio)
boton2.SetToolTip('Cambia el radio de todos los átomos del elemento seleccionado')

RE = wx.TextCtrl(panel,pos = (265,290+y3), size = (40,20),value = '0.10',style = wx.TE_PROCESS_ENTER)
RE.Bind(wx.EVT_TEXT_ENTER,ActTodosEn)

boton4 = wx.Button(panel, label='Cambiar radio de\ntodos los enlaces', pos=(310,290+y3),size=(125,35))
boton4.Bind(wx.EVT_BUTTON,ActTodosEn)
boton4.SetToolTip('Cambia el radio de todos los enlaces')

boton6 = wx.Button(panel, label='Radios\noriginales', pos=(135,325+y3),size=(100,35))
boton6.Bind(wx.EVT_BUTTON,Originales)

DicTxt  = {'CR1':St1,    'CR2':St2,    'CR3':St3}
DicFun1 = {'CR1':K,      'CR2':En,     'CR3':Ne}
DicTxt1 = {'CR1':RadEnT1,'CR2':RadEnT2,'CR3':RadEnT3}

filemenu = wx.Menu()
filemenu.Append(101, 'Leer XYZ')
filemenu.Append(102, 'Leer MOL')
filemenu.Append(103, 'Exportar STL')
filemenu.Append(104, 'Exportar Imagen')
filemenu.Append(105, 'Leer Escena')
filemenu.Append(106, 'Salvar Escena')

menuBar = wx.MenuBar()
menuBar.Append(filemenu,'Archivo') 
frame.SetMenuBar(menuBar)  

filemenu.Bind(wx.EVT_MENU, XYZR,      id = 101)
filemenu.Bind(wx.EVT_MENU, MOLR,      id = 102)
filemenu.Bind(wx.EVT_MENU, STLG,      id = 103)
filemenu.Bind(wx.EVT_MENU, SPNG,      id = 104)
filemenu.Bind(wx.EVT_MENU, LeerPAS,   id = 105)
filemenu.Bind(wx.EVT_MENU, SalvarPAS, id = 106)

VE  = LeeSTL('ES.rem')
VC  = LeeSTL('CIL.rem')
VC2 = LeeSTL('doble.rem')
VC3 = LeeSTL('triple.rem')

ListaRadios()
Depura()

K.SetCheckedItems([0])
seccion(1)

frame.Show()
plotter.show(interactive=True)
app.MainLoop()
