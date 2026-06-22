import wx
import re

class PyAtomSTLFrame(wx.Frame):
    def __init__(self, main_app):
        super().__init__(None, title='PyAtomSTL', size=(560, 520))
        self.main = main_app  
        self.panel = wx.Panel(self)
        self.init_ui()

    def init_ui(self):
        y1 = 5; y2 = 20; y3 = 20

        self.Vista = wx.CheckBox(self.panel, pos=(5, 15+y1), label='Perspectiva')
        self.Vista.SetValue(True)
        self.Vista.Bind(wx.EVT_CHECKBOX, self.main.vista)

        self.M1 = wx.CheckBox(self.panel, pos=(320, 5+y1), label='Símbolo')
        self.M1.SetValue(True)
        self.M1.Bind(wx.EVT_CHECKBOX, self.main.act_etiquetas)

        self.M2 = wx.CheckBox(self.panel, pos=(320, 25+y1), label='Indices')
        self.M2.SetValue(True)
        self.M2.Bind(wx.EVT_CHECKBOX, self.main.act_etiquetas)

        self.Ej = wx.CheckBox(self.panel, pos=(410, 15+y1), label='Ejes')
        self.Ej.SetValue(True)
        self.Ej.Bind(wx.EVT_CHECKBOX, self.main.act_ejes)

        self.K1 = wx.StaticBox(self.panel, pos=(90, 0+y1), label='Rotar Sobre:', size=(190, 36))
        self.R1 = wx.RadioButton(self.panel, pos=(100, 15+y1), label='<0,0,0>')
        self.R2 = wx.RadioButton(self.panel, pos=(180, 15+y1), label='Centro Geom')
        self.R1.Bind(wx.EVT_RADIOBUTTON, self.main.setorigen)
        self.R2.Bind(wx.EVT_RADIOBUTTON, self.main.setorigen)
        self.R2.SetValue(True)

        self.St1 = wx.CheckBox(self.panel, pos=(5, 70+y1), label='', name='CR1')
        self.St2 = wx.CheckBox(self.panel, pos=(150, 70+y1), label='', name='CR2')
        self.St3 = wx.CheckBox(self.panel, pos=(295, 70+y1), label='', name='CR3')
        for cb in [self.St1, self.St2, self.St3]:
            cb.Bind(wx.EVT_CHECKBOX, self.main.SelTodos) # Seleccionar todos los enlaces de cada lista

        self.K = wx.CheckListBox(self.panel, pos=(5, 70+y2), size=(123, 120), choices=self.main.DisStr, name='CR1')
        self.K.Bind(wx.EVT_CHECKLISTBOX, self.main.seccion)
        self.K.Bind(wx.EVT_LISTBOX, self.main.CRadioE)

        self.En = wx.CheckListBox(self.panel, pos=(150, 70+y2), size=(130, 120), choices=[], name='CR2')
        self.En.Bind(wx.EVT_CHECKLISTBOX, self.main.DibujaEnlaces)
        self.En.Bind(wx.EVT_LISTBOX, self.main.CRadioE)

        self.Ne = wx.CheckListBox(self.panel, pos=(295, 70+y2), size=(130, 120), choices=[], name='CR3')
        self.Ne.Bind(wx.EVT_CHECKLISTBOX, self.main.DibujaEnlaces)
        self.Ne.Bind(wx.EVT_LISTBOX, self.main.CRadioE)

        self.boton = wx.Button(self.panel, label='Agregar enlace\nentre átomos:', pos=(430, 70+y2), size=(95, 35))
        self.boton.Bind(wx.EVT_BUTTON, self.main.NuevoEnlace)

        self.T1 = wx.TextCtrl(self.panel, pos=(430, 110+y2), size=(44, 18))
        self.T2 = wx.TextCtrl(self.panel, pos=(480, 110+y2), size=(44, 18))

        self.boton1 = wx.Button(self.panel, label='Borrar Lista', pos=(430, 166+y2), size=(87, 24))
        self.boton1.Bind(wx.EVT_BUTTON, self.main.Borrar)

        self.RadEnT1 = wx.TextCtrl(self.panel, pos=(5, 192+y2), size=(40, 22), value='0.10', style=wx.TE_PROCESS_ENTER)
        self.RadEnB1 = wx.Button(self.panel, pos=(45, 190+y2), size=(85, 25), label='Cambiar radio', name='CR1')

        self.RadEnT2 = wx.TextCtrl(self.panel, pos=(150, 192+y2), size=(40, 22), value='0.10', style=wx.TE_PROCESS_ENTER)
        self.RadEnB2 = wx.Button(self.panel, pos=(190, 190+y2), size=(92, 25), label='Cambiar radio', name='CR2')

        self.RadEnT3 = wx.TextCtrl(self.panel, pos=(295, 192+y2), size=(40, 22), value='0.10', style=wx.TE_PROCESS_ENTER)
        self.RadEnB3 = wx.Button(self.panel, pos=(335, 190+y2), size=(92, 25), label='Cambiar radio', name='CR3')

        for btn in [self.RadEnB1, self.RadEnB2, self.RadEnB3]:
            btn.Bind(wx.EVT_BUTTON, self.main.CambiarRadioE)
        
        self.RadEnB1.SetToolTip('Cambia el radio de todos los enlaces con la longitud seleccionada')
        self.RadEnB2.SetToolTip('Cambia el radio del enlace seleccionado')
        self.RadEnB3.SetToolTip('Cambia el radio del enlace seleccionado')

        self.BTD1 = wx.Button(self.panel, pos=(5, 220+y2),  size=(85, 25),  label='Enlace S/D/T', name='CR1')
        self.BTD2 = wx.Button(self.panel, pos=(150, 220+y2), size=(85, 25), label='Enlace S/D/T', name='CR2')
        self.BTD3 = wx.Button(self.panel, pos=(295, 220+y2), size=(85, 25), label='Enlace S/D/T', name='CR3')

        for btn in [self.BTD1, self.BTD2, self.BTD3]:
            btn.Bind(wx.EVT_BUTTON, self.main.DSE)
            btn.SetToolTip('Enlace sencillo/doble/triple')

        self.L2 = wx.StaticText(self.panel, pos=(5, 40+y2),   label='Long. enlace - Radio')
        self.L3 = wx.StaticText(self.panel, pos=(150, 40+y2), label='Enlace: At1, At2 - Radio')
        self.L4 = wx.StaticText(self.panel, pos=(295, 40+y2), label='Enlace: At1, At2 - Radio')

        wx.StaticLine(self.panel, pos=(5, 260+y3), size=(530, 2), style=wx.LI_HORIZONTAL)
        self.L1 = wx.StaticText(self.panel, pos=(5, 270+y3), label='Átomo - Radio')

        self.At = wx.ListBox(self.panel, pos=(5, 290+y3), size=(80, 120), choices=[])
        self.At.Bind(wx.EVT_LISTBOX, self.main.CRadio)

        self.Ar = wx.TextCtrl(self.panel, pos=(90, 290+y3), size=(40, 20), value='', style=wx.TE_PROCESS_ENTER)
        self.Ar.Bind(wx.EVT_TEXT_ENTER, self.main.CambiarRadio)

        self.boton2 = wx.Button(self.panel, label='Cambiar radio\ndel átomo', pos=(135, 290+y3), size=(100, 35))
        self.boton2.Bind(wx.EVT_BUTTON, self.main.CambiarRadio)
        self.boton2.SetToolTip('Cambia el radio de todos los átomos del elemento seleccionado')

        self.boton3 = wx.Button(self.panel, label='Cambiar color\ndel fondo', pos=(310, 345+y3), size=(100, 35))
        self.boton3.Bind(wx.EVT_BUTTON, self.main.Fondo)
        self.boton3.SetToolTip('Permite seleccionar el color del fondo')

        self.RE = wx.TextCtrl(self.panel, pos=(265, 290+y3), size=(40, 20), value='0.10', style=wx.TE_PROCESS_ENTER)
        self.RE.Bind(wx.EVT_TEXT_ENTER, self.main.ActTodosEn)

        self.boton4 = wx.Button(self.panel, label='Cambiar radio de\ntodos los enlaces', pos=(310, 290+y3), size=(125, 35))
        self.boton4.Bind(wx.EVT_BUTTON, self.main.ActTodosEn)
        self.boton4.SetToolTip('Cambia el radio de todos los enlaces')

        self.boton5 = wx.Button(self.panel, label='Visualizar\n3D Rojo/Cyan', pos=(310, 385 + y3), size=(100, 35))
        self.boton5.Bind(wx.EVT_BUTTON, self.main.Anaglyph)
        self.boton5.SetToolTip('Cambia la visualización a anaglifo rojo/cyan')

        self.boton6 = wx.Button(self.panel, label='Radios\noriginales', pos=(135, 325+y3), size=(100, 35))
        self.boton6.Bind(wx.EVT_BUTTON, self.main.Originales)

        filemenu = wx.Menu()
        filemenu.Append(101, 'Leer XYZ')
        filemenu.Append(102, 'Leer MOL')
        filemenu.Append(103, 'Exportar STL')
        filemenu.Append(104, 'Exportar Imagen')
        filemenu.Append(105, 'Leer Escena')
        filemenu.Append(106, 'Salvar Escena')

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, 'Archivo') 
        self.SetMenuBar(menuBar)  

        self.Bind(wx.EVT_MENU, self.main.XYZR, id=101)
        self.Bind(wx.EVT_MENU, self.main.MOLR, id=102)
        self.Bind(wx.EVT_MENU, self.main.STLG, id=103)
        self.Bind(wx.EVT_MENU, self.main.SPNG, id=104)
        self.Bind(wx.EVT_MENU, self.main.LeerPAS, id=105)
        self.Bind(wx.EVT_MENU, self.main.SalvarPAS, id=106)

    def crear_diccionarios(self):
        self.DicTxt  = {'CR1': self.St1,    'CR2': self.St2,    'CR3': self.St3}
        self.DicFun1 = {'CR1': self.K,      'CR2': self.En,     'CR3': self.Ne}
        self.DicTxt1 = {'CR1': self.RadEnT1,'CR2': self.RadEnT2,'CR3': self.RadEnT3}
