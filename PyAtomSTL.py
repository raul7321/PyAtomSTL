import pyvista as pv
from ChemFun import *
import wx
import re as re
import numpy as np
import vtkmodules.vtkRenderingCore as vtk_core
import sys
from Atom_panel import PyAtomSTLFrame

plotter = pv.Plotter()
plotter.set_background('black')
plotter.enable_lightkit()
plotter.add_axes()

REG1 = r'^(\d+),(\d+)\s-\s(\d*\.?\d*)\s*([DT]*)$'
REG2 = r'^([a-zA-Z]+)'+3*r'\s+(\-?\d*\.?\d*e?\-?\d*)'+r'\s*$'
REG3 = r'^(\d*\.?\d*)\s*-\s*(\d*\.?\d*)\s*([DT]*)$'
REG5 = r'^'+3*r'(\-?\d*\.?\d*e?\-?\d*)\s+'+'([A-Z][a-z]*)'
REG6 = r'^(\d+)\s+(\d+)\s+(\d+)'

class Atomo():
    def __init__(self, ind, sym, pos):
        self.indice = (str(ind)).zfill(3)
        self.simbolo = sym
        self.posicionVis = np.array([float(k) for k in pos])
        self.colorVis = GetColor(sym)
        self.radio = GetRadius(sym) / 2

def Borrar(event):
    ui.Ne.Clear()
    DibujaEnlaces(None)

def vista(event):
    plotter.camera.disable_parallel_projection() if ui.Vista.Value else plotter.camera.enable_parallel_projection()
    
def NuevoEnlace(event):
    if ui.T1.Value != ui.T2.Value and str(ui.T1.Value).isdigit() and str(ui.T2.Value).isdigit():
        t = str(ui.T1.Value).zfill(3) + ',' + str(ui.T2.Value).zfill(3)
        t1 = set([str(ui.T1.Value).zfill(3), str(ui.T2.Value).zfill(3)])
        
        k1 = [set((h.split(' - ')[0]).split(',')) for h in ui.En.GetStrings()]
        k2 = [set((h.split(' - ')[0]).split(',')) for h in ui.Ne.GetStrings()]
        if (t1 in k1) or (t1 in k2):
            dlg = wx.MessageDialog(ui.panel, 'Ese enlace ya está en el sistema.', 'PyAtomSTL', wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            t = t + ' - 0.10'
            ui.Ne.Append(t)
            ui.Ne.SetCheckedStrings([t])
            DibujaEnlaces(None)

def DibujaEnlaces(event):
    for actor_name in list(plotter.actors.keys()):
        if actor_name.startswith('cil_'):
            plotter.remove_actor(actor_name)
    C = []
    for n in [ui.En.GetCheckedStrings(), ui.Ne.GetCheckedStrings()]:
        for z1 in n:
            [e0, e1, r, d] = [f(x) for f, x in zip([int, int, float, str], [re.search(REG1, z1).group(h) for h in range(1, 5)])]
            k1, k2 = Atomos[e0].posicionVis, Atomos[e1].posicionVis
            centro = (k1 + k2) / 2.0
            direccion = k2 - k1
            longitud = np.linalg.norm(direccion)
            
            per = np.array([direccion[2], 0, -direccion[0]])
            if np.linalg.norm(per) != 0:
                per = per / np.linalg.norm(per)
                
            if d == 'D':
                Cil = pv.Cylinder(center=centro + per*1.2*r, direction=direccion, height=longitud, radius=r)
                C.append(Cil.extract_surface(algorithm='dataset_surface'))
                Cil = pv.Cylinder(center=centro - per*1.2*r, direction=direccion, height=longitud, radius=r)
                C.append(Cil.extract_surface(algorithm='dataset_surface'))
            elif d == 'T':
                Cil = pv.Cylinder(center=centro, direction=direccion, height=longitud, radius=r)
                C.append(Cil.extract_surface(algorithm='dataset_surface'))
                Cil = pv.Cylinder(center=centro + per*3.0*r, direction=direccion, height=longitud, radius=r)
                C.append(Cil.extract_surface(algorithm='dataset_surface'))
                Cil = pv.Cylinder(center=centro - per*3.0*r, direction=direccion, height=longitud, radius=r)
                C.append(Cil.extract_surface(algorithm='dataset_surface'))
            else:
                Cil = pv.Cylinder(center=centro, direction=direccion, height=longitud, radius=r)
                C.append(Cil.extract_surface(algorithm='dataset_surface'))
    C = pv.MultiBlock(C)

    plotter.add_mesh(
        C, color='white',
        smooth_shading=True,
        name='enlaces_moleculares',
        render=False
    )
    
def ActualizaPAS():
    global Atomos
    DibujaEnlaces(None)

def Repetidos():
    k1 = [set((h.split(' - ')[0]).split(',')) for h in ui.En.GetStrings()]
    k2 = [set((h.split(' - ')[0]).split(',')) for h in ui.Ne.GetStrings()]
    R = [i for i, h2 in enumerate(k2) if h2 in k1]
    R.sort(reverse = True)
    return R

def RenderVista():
    global Atomos,esfera,puntos
    fs = 20; fi = 15
    plotter.enable_lightkit()

    posiciones = np.array([a.posicionVis for a in Atomos])
    radios = np.array([a.radio for a in Atomos])
    colores = np.array([a.colorVis for a in Atomos], dtype=np.uint8) 

    puntos = pv.PolyData(posiciones)

    puntos['radios']  = radios
    puntos['colores'] = colores

    esfera = pv.Sphere(radius = 1.0, theta_resolution = 20, phi_resolution = 20)

    glifos_atomos = puntos.glyph(geom  = esfera, scale = 'radios', orient = False, tolerance = 0.0)

    plotter.add_mesh(
        glifos_atomos,
        scalars = 'colores',  
        rgb = True,                  
        smooth_shading = True,       
        ambient = 0.3,
        specular = 0.5,
        name = 'atomos'   
    )

    for a in Atomos:
        pos_simbolo = a.posicionVis + np.array([a.radio * 1.25,  a.radio * 1.25, 0])
        pos_indice =  a.posicionVis + np.array([a.radio * 1.25, -a.radio * 1.25, 0])
        
        sim_texto = vtk_core.vtkBillboardTextActor3D()
        sim_texto.SetInput(a.simbolo)
        sim_texto.SetPosition(pos_simbolo)
        
        texto = vtk_core.vtkBillboardTextActor3D()
        texto.SetInput(str(a.indice))  
        texto.SetPosition(pos_indice)
        
        p_sim = sim_texto.GetTextProperty()
        p_sim.SetFontSize(fs)      
        p_sim.SetColor(1.0, 1.0, 1.0) 
        p_sim.SetJustificationToCentered()  
        p_sim.BoldOn()
        p_sim.ShadowOn()
        
        p_idx = texto.GetTextProperty()
        p_idx.SetFontSize(fi)      
        p_idx.SetColor(1.0, 1.0, 1.0) 
        p_idx.SetJustificationToCentered()  

        plotter.add_actor(sim_texto, name = f'S_{a.indice}_{a.simbolo}')
        plotter.add_actor(texto, name = f'I_{a.indice}_{a.simbolo}')

def RenuevaAtomos():
    global Atomos, esfera, puntos

    radios = np.array([a.radio for a in Atomos])
    puntos['radios'] = radios
    glifos_atomos = puntos.glyph(geom = esfera, scale='radios', orient=False, tolerance=0.0)

    plotter.add_mesh(
        glifos_atomos,
        scalars='colores',
        rgb=True,
        smooth_shading=True,
        ambient=0.3,
        specular=0.5,
        name='atomos'
    )

    for n in list(plotter.actors.keys()):
        if n.startswith('S_') or n.startswith('I_'):
            i = int(n.split('_')[1])
            pos_simbolo = Atomos[i].posicionVis + np.array([Atomos[i].radio * 1.25, Atomos[i].radio * 1.25, 0])
            pos_indice  = Atomos[i].posicionVis + np.array([Atomos[i].radio * 1.25, -Atomos[i].radio * 1.25, 0])

            k = pos_simbolo if n.startswith('S_') else pos_indice
            plotter.actors[n].SetPosition(*k)
        
def Actualiza(SD, Dis, rad_en):
    global CM, muestra, Atomos
    
    Z = []
    for sd, r, D in zip(SD, rad_en, Dis):
        Enlaces = []
        for i in Atomos:
            for j in Atomos:
                if abs(np.linalg.norm(i.posicionVis - j.posicionVis) - D) < D / 100:
                    Enlaces.append(frozenset([i.indice, j.indice]))
        Enlaces = [list(e) for e in list(set(Enlaces))]
        for e in Enlaces:
            Z.append(str(e[0]) + ',' + str(e[1]) + ' - ' + str(r) + sd)
            
    Z.sort()
    ui.En.Clear()
    ui.En.Append(Z)
    ui.En.SetCheckedItems(range(len(Z)))

    for r in Repetidos(): ui.Ne.Delete(r)
    
    if muestra:
        CM = np.array([0.0, 0.0, 0.0])
        for a in Atomos:
            CM = CM + a.posicionVis
        CM = CM / len(Atomos)
        plotter.clear()
        RenderVista()
        DibujaEnlaces(None)
    
def setorigen(event):
    global CM
    plotter.camera.focal_point = [0.0, 0.0, 0.0] if ui.R1.GetValue() else [CM[0], CM[1], CM[2]]
    plotter.render()
    
def seccion(event):
    Z = ui.K.GetCheckedStrings()
    K0 = [re.search(REG3, k).group(3) for k in Z]
    K1 = [float(re.search(REG3, k).group(1)) for k in Z]
    K2 = [float(re.search(REG3, k).group(2)) for k in Z]
    Actualiza(K0, K1, K2)
    
def act_etiquetas(event):
    Ms, Mi = ui.M1.GetValue(), ui.M2.GetValue()
    for n in list(plotter.actors.keys()):
        if n.startswith('S_'): plotter.actors[n].visibility = Ms
        if n.startswith('I_'): plotter.actors[n].visibility = Mi
    plotter.render()  

def act_ejes(event):
    plotter.add_axes() if ui.Ej.GetValue() else plotter.hide_axes()

def Inicia(name):
    global DisStr, Atomos, muestra
    muestra = 0; LA = []
    for a in [a.strip() for a in list(open(name, 'r'))]:
        if re.search(REG2, a):
            res = re.search(REG2, a)
            LA.append([res.group(1), [float(res.group(i)) for i in range(2, 5)]])
    Atomos = [Atomo(i, a[0], a[1]) for i, a in enumerate(LA)]
    Distancias = []
    for i in Atomos:
        disT = []
        for j in Atomos:
            if i.indice != j.indice:
                disT.append(round(np.linalg.norm(i.posicionVis - j.posicionVis), 3))
        disT.sort(); mk = disT[0]
        disT = [k for k in disT if k <= 1.5 * mk]
        Distancias.extend(disT)
    Distancias = list(set(Distancias))
    Distancias.sort()
    DisStr = [str(t) + ' - 0.10' for t in Distancias]

def IniciaMOL(name):
    global DisStr, Atomos, muestra
    muestra = 0; LA = []; Emol = []
    A = [a.strip() for a in list(open(name, 'r'))]
    for a in A:
        if re.search(REG5, a):
            res = re.search(REG5, a)
            LA.append([res.group(4), [float(res.group(i)) for i in range(1, 4)]])
        if re.search(REG6, a) and len(LA) != 0:
            res = re.search(REG6, a)
            e1 = str(int(res.group(1)) - 1)
            e2 = str(int(res.group(2)) - 1)
            Emol.append(e1.zfill(3) + ',' + e2.zfill(3) + ' - 0.1 ' + ['', '', 'D', 'T'][int(res.group(3))])
    Atomos = [Atomo(i, a[0], a[1]) for i, a in enumerate(LA)]
    Distancias = []
    for i in Atomos:
        disT = []
        for j in Atomos:
            if i.indice != j.indice:
                disT.append(round(np.linalg.norm(i.posicionVis - j.posicionVis), 3))
        disT.sort(); mk = disT[0]
        disT = [k for k in disT if k <= 1.5 * mk]
        Distancias.extend(disT)
    Distancias = list(set(Distancias))
    Distancias.sort()
    DisStr = [str(t) + ' - 0.10' for t in Distancias]
    return Emol

def Depura():
    global muestra
    R = []; Repetidos = []; K1 = ui.K.GetItems()
    for i, k in enumerate(K1):
        ui.K.SetCheckedItems([i])
        seccion(None)
        E1 = ui.En.GetItems()
        ya = 0
        for r in R:
            if E1[0] in r:
                Repetidos.append(i)
                ya = 1; break
        if ya == 0: R.append(E1)
    ui.K.Clear()
    for i, k in enumerate(K1):
        if i not in Repetidos: ui.K.Append(k)
    muestra = 1

def STL(nam):
    print("Exportando STL...")

def CRadio(event):
    k = ui.At.GetString(ui.At.GetSelection())
    k = k.split(' - ')
    ui.Ar.Value = k[1]

def CRadioE(event):
    B_id = event.GetEventObject().GetName()
    k = ui.DicFun1[B_id].GetString(ui.DicFun1[B_id].GetSelection()).replace(' D', '')
    k = k.replace(' T', '')
    k = k.split(' - ')
    ui.DicTxt1[B_id].Value = k[1]

def ActTodosEn(event):
    re_val = ui.RE.Value.strip()
    
    seK = ui.K.GetCheckedItems()
    K1 = [k.split(' - ')[0] + ' - ' + re_val for k in ui.K.GetItems()]
    ui.K.SetItems(K1)
    ui.K.SetCheckedItems(seK)

    seK = ui.En.GetCheckedItems()
    K1 = [k.split(' - ')[0] + ' - ' + re_val for k in ui.En.GetItems()]
    ui.En.SetItems(K1)
    ui.En.SetCheckedItems(seK)

    seK = ui.Ne.GetCheckedItems()
    K1 = [k.split(' - ')[0] + ' - ' + re_val for k in ui.Ne.GetItems()]
    ui.Ne.SetItems(K1)
    ui.Ne.SetCheckedItems(seK)
    
    DibujaEnlaces(None)

def CambiarRadio(event):
    try:
        k = ui.At.GetString(ui.At.GetSelection())
        k = k.split(' - ')
        ui.At.SetString(ui.At.GetSelection(), k[0] + ' - ' + str(float(ui.Ar.Value)))
        for a in Atomos:
            if a.simbolo == k[0]: a.radio = float(ui.Ar.Value)
        RenuevaAtomos()
        #seccion(None)
    except:
        dlg = wx.MessageDialog(ui.panel, 'Debes resaltar una entrada de la lista\ny dar un radio válido', 'PyAtomSTL', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def CambiarRadioE(event):
    global muestra
    try:
        B_id = event.GetEventObject().GetName()
        h = ui.DicFun1[B_id].GetString(ui.DicFun1[B_id].GetSelection())
        dt = (h.strip())[-1] if ('D' in h or 'T' in h) else ''
        k = h.split(' - ')
        ui.DicFun1[B_id].SetString(ui.DicFun1[B_id].GetSelection(), k[0] + ' - ' + str(float(ui.DicTxt1[B_id].Value)) + ' ' + dt) 
        muestra = False
        if B_id == 'CR1': seccion(None)
        DibujaEnlaces(None)
        muestra = True
    except:
        dlg = wx.MessageDialog(ui.panel, 'Debes resaltar una entrada de la lista!', 'PyAtomSTL', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def DSE(event):
    global muestra
    try:
        B_id = event.GetEventObject().GetName()
        k = ui.DicFun1[B_id].GetString(ui.DicFun1[B_id].GetSelection())
        if 'D' in k:
            ui.DicFun1[B_id].SetString(ui.DicFun1[B_id].GetSelection(), k.replace('D', 'T'))
        elif 'T' in k:
            ui.DicFun1[B_id].SetString(ui.DicFun1[B_id].GetSelection(), k.replace('T', ''))
        else:
            ui.DicFun1[B_id].SetString(ui.DicFun1[B_id].GetSelection(), k + ' D')
        muestra = False
        if B_id == 'CR1': seccion(None)
        DibujaEnlaces(None)
        muestra = True
    except:
        dlg = wx.MessageDialog(ui.panel, 'Debes resaltar una entrada de la lista!', 'PyAtomSTL', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

def STLG(event):
    global ruta
    nam = re.search(r'(^[A-Z]:)*(\\.+)*\\(.+)\..+', ruta).group(3)
    fileDialog = wx.FileDialog(ui.panel, "Exportar archivo STL", wildcard="Archivo STL (*.stl)|*.stl", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    fileDialog.SetFilename(nam)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ruta = fileDialog.GetPath()
    STL(ruta)

def XYZR(event):
    global DisStr, ruta
    fileDialog = wx.FileDialog(ui.panel, "Leer archivo XYZ", wildcard="Archivo XYZ (*.xyz)|*.xyz", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ui.RE.value = '0.10'
    ruta = fileDialog.GetPath()
    Inicia(ruta)
    ui.K.SetItems(DisStr)
    ui.En.SetItems([])
    ui.Ne.SetItems([])
    Depura()
    ui.K.SetCheckedItems([0])
    ListaRadios()
    seccion(None)
    
def MOLR(event):
    global DisStr, ruta
    fileDialog = wx.FileDialog(ui.panel, "Leer archivo MOL", wildcard="Archivo MOL (*.mol)|*.mol", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ui.RE.value = '0.10'
    ruta = fileDialog.GetPath()
    Emol = IniciaMOL(ruta)
    ui.K.SetItems(DisStr)
    ui.En.SetItems([])
    Depura()
    ui.Ne.SetItems(Emol)
    ui.Ne.SetCheckedItems(range(len(ui.Ne.GetStrings())))
    ListaRadios()
    seccion(None)

def ListaRadios():
    AtS = []; ui.At.SetItems([])
    for a in Atomos:
        if a.simbolo not in AtS:
            ui.At.Append(a.simbolo + ' - ' + str(a.radio))
            AtS.append(a.simbolo)

def Originales(event):
    for a in Atomos: a.radio = GetRadius(a.simbolo) / 2.0
    ListaRadios()
    RenuevaAtomos()

def LeerPAS(event):
    global ruta, muestra, Atomos
    fileDialog = wx.FileDialog(ui.panel, "Leer archivo PAS", wildcard='Archivo PAS (*.pas)|*.pas', style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ruta = fileDialog.GetPath()
    ui.K.Clear(); ui.En.Clear(); ui.Ne.Clear(); ui.At.Clear()
    Atomos = []
    archivo = list(open(ruta, 'r'))
    for a in archivo:
        k = a.split(',')
        if k[0] == '@1':
            res = re.search(r'<(\-?\d*\.?\d*e?\-?\d*),\s?(\-?\d*\.?\d*e?\-?\d*),\s?(\-?\d*\.?\d*e?\-?\d*)', a)
            r1, r2, r3 = float(res.group(1)), float(res.group(2)), float(res.group(3))
            Atomos.append(Atomo(int(k[1]), k[2], [r1, r2, r3]))
        if k[0] == '@2':
            ui.At.Append(k[1] + ' - ' + k[2])
            for atom in Atomos:
                if atom.simbolo == k[1]: atom.radio = float(k[2])
        if k[0] == '@3':
            ui.K.Append(k[1] + ' - ' + k[2] + k[3])
        if k[0] == '@4':
            res = re.search(r'\((.*)\)', k[1])
            ui.K.SetCheckedItems([int(h) for h in res.group(1).split()])
        if k[0] == '@5':
            ui.En.Append(k[1].zfill(3) + ',' + k[2].zfill(3) + ' - ' + k[3] + ' ' + k[4])
        if k[0] == '@6':
            res = re.search(r'\((.*)\)', k[1])
            ui.En.SetCheckedItems([int(h) for h in res.group(1).split()])
        if k[0] == '@7':
            ui.Ne.Append(k[1].zfill(3) + ',' + k[2].zfill(3) + ' - ' + k[3] + ' ' + k[4])
        if k[0] == '@8':
            res = re.search(r'\((.*)\)', k[1])
            ui.Ne.SetCheckedItems([int(h) for h in res.group(1).split()])
    ActualizaPAS()
    ui.K.Enabled = True

def SalvarPAS(event):
    global ruta
    nam = re.search(r'(^[A-Z]:)*(\\.+)*\\(.+)\..+', ruta).group(3)
    fileDialog = wx.FileDialog(ui.panel, "Salvar archivo PAS", wildcard="Archivo PAS (*.pas)|*.pas", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    fileDialog.SetFilename(nam)
    if fileDialog.ShowModal() == wx.ID_CANCEL: return
    ruta = fileDialog.GetPath()
    salva = open(ruta, 'w')
    for a in Atomos:
        salva.write('@1,' + a.indice + ',' + a.simbolo + ',' + str(a.posicionVis) + '\n')
    for a in ui.At.GetItems():
        k = a.split(' - '); salva.write('@2,' + k[0] + ',' + k[1].strip() + '\n')
    for a in ui.K.GetItems():
        dt = (a.strip())[-1] if ('D' in a or 'T' in a) else ''
        k = a.split(' - '); salva.write('@3,' + k[0] + ',' + k[1].strip() + ',' + dt + '\n')
    salva.write('@4,' + str(ui.K.GetCheckedItems()).replace(',', '') + '\n')
    for a in ui.En.GetItems():
        dt = (a.strip())[-1] if ('D' in a or 'T' in a) else ''
        a = a.replace('D', ''); a = a.replace('T', '')
        k = a.split(' - ')
        salva.write('@5,' + k[0] + ',' + k[1] + ',' + dt + '\n')
    salva.write('@6,' + str(ui.En.GetCheckedItems()).replace(',', '') + '\n')
    for a in ui.Ne.GetItems():
        dt = (a.strip())[-1] if ('D' in a or 'T' in a) else ''
        a = a.replace('D', ''); a = a.replace('T', '')
        k = a.split(' - ')
        salva.write('@7,' + k[0] + ',' + k[1].strip() + ',' + dt + '\n')
    salva.write('@8,' + str(ui.Ne.GetCheckedItems()).replace(',', '') + '\n')
    salva.close()

def SelTodos(event):
    B_id = event.GetEventObject().GetName()
    ui.DicFun1[B_id].SetCheckedItems(range(len(ui.DicFun1[B_id].GetItems())) if ui.DicTxt[B_id].GetValue() else [])
    if B_id == 'CR1':
        seccion(None)
    else:
        DibujaEnlaces(None)

def SPNG(event):
    print('Capturando Imagen...')

app = wx.App()

ruta = r'\CuCl.xyz'

try:
    Inicia(ruta[1:])
except FileNotFoundError:
    DisStr = []
    Atomos = []

ui = PyAtomSTLFrame(main_app=sys.modules[__name__])
ui.crear_diccionarios()

ListaRadios()
Depura()
ui.K.SetCheckedItems([0])
seccion(None)

ui.Show()
plotter.show(interactive = True)

app.MainLoop()

