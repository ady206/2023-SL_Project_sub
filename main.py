from tkinter import *
import tkinter.ttk as ttk
import tkinter.font
import urllib
import urllib.request
import requests
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk
import io
from googlemaps import Client
import threading
import sys
from tkintermapview import TkinterMapView
from cefpython3 import cefpython as cef
import random
import teller
import spam
from tkinter import filedialog

# window -------------------------------------------------------------------------------------------
class MainGUI():
    HeritageTotalList = []
    HeritageList = []
    pageIndex = 1
    zoom = 15
    markercnt = 0

    heritage_names = []
    def appendList(self, List):
        for item in self.items:
            heritage = {
                "type": item.findtext("ccmaName"),
                "CtcdNm": item.findtext("ccbaCtcdNm"),
                "siName": item.findtext("ccsiName"),
                "name": item.findtext("ccbaMnm1"),
                "ccbaAdmin" : item.findtext("ccbaAdmin"),
                "ccbaKdcd": item.findtext("ccbaKdcd"),
                "ccbaCtcd": item.findtext("ccbaCtcd"),
                "ccbaAsno": item.findtext("ccbaAsno"),
            }
            List.append(heritage)

    def heritage_image_url(self):
        index = int(self.item)
        ccbakdcd = self.HeritageTotalList[index]['ccbaKdcd']
        ccbaasno = self.HeritageTotalList[index]['ccbaAsno']
        ccbactcd = self.HeritageTotalList[index]['ccbaCtcd']

        self.Iurl = 'http://www.cha.go.kr/cha/SearchImageOpenapi.do?ccbaKdcd=' + ccbakdcd + '&ccbaAsno=' + ccbaasno + '&ccbaCtcd=' + ccbactcd
        self.Iresponse = requests.get(self.Iurl)
        self.Iroot = ET.fromstring(self.Iresponse.text)

        self.range = 10
        self.Iimage = self.Iroot.findall(".//item//imageUrl")[:self.range]
        self.Iscript = self.Iroot.findall('.//item//ccimDesc')[:self.range]

    def heritage_map_url(self):
        index = int(self.item)
        self.ccbaMnm1 = self.HeritageTotalList[index]['name']

        self.Google_API_Key = 'AIzaSyDLedLGEpRdNWyvw7vgySIpaftbxlqfzwA'
        self.gmaps = Client(key = self.Google_API_Key)
        self.center = self.gmaps.geocode(self.ccbaMnm1)[0]['geometry']['location']
        self.lat, self.lng = float(self.center['lat']), float(self.center['lng'])

    def heritage_content_url(self):
        index = int(self.item)
        ccbakdcd = self.HeritageTotalList[index]['ccbaKdcd']
        ccbaasno = self.HeritageTotalList[index]['ccbaAsno']
        ccbactcd = self.HeritageTotalList[index]['ccbaCtcd']

        self.Curl = 'http://www.cha.go.kr/cha/SearchKindOpenapiDt.do?ccbaKdcd=' + ccbakdcd + '&ccbaAsno=' + ccbaasno + '&ccbaCtcd=' + ccbactcd
        self.Cresponse = requests.get(self.Curl)
        self.Croot = ET.fromstring(self.Cresponse.text)

        self.CimageUrl = self.Croot.findtext(".//item//imageUrl")
        self.Ccontent = self.Croot.findtext('.//item//content')

    def set_heritage(self):
        for i in range(17):
            self.url = 'http://www.cha.go.kr/cha/SearchKindOpenapiList.do?pageUnit=1000&pageIndex=' + str(self.pageIndex + i)
            self.response = requests.get(self.url)
            self.root = ET.fromstring(self.response.text)
            self.items = self.root.findall(".//item")
            self.appendList(self.HeritageTotalList)

    # -----------------------------------------------------------------------------------------------

    def show_image(self):
        self.heritage_image_url()
        self.new_window = Toplevel(bg = 'white')
        self.new_window.title(str(self.iid) + '번 결과 이미지 정보')
        self.image_window = ttk.Notebook(self.new_window, width=800, height=600)
        self.image_window.pack()

        self.image_item_list = []

        if self.range > len(self.Iimage): self.range = len(self.Iimage)
        for i in range(self.range):
            with urllib.request.urlopen(self.Iimage[i].text) as u:
                raw_data = u.read()
            im = Image.open(io.BytesIO(raw_data))
            self.photo = ImageTk.PhotoImage(im)
            self.image_item_list.append([self.Iscript[i].text, self.photo])

        for i in range(self.range):
            frame = Frame(self.new_window)
            self.image_window.add(frame, text = str(i + 1))
            Label(frame, text = self.image_item_list[i][0], font = self.fontstyle1).pack(side = TOP, anchor = CENTER)
            Label(frame, text = '* 상위 10개 항목만 표시합니다', font = self.fontstyle3).pack(side = TOP, anchor = NE)
            Label(frame, image = self.image_item_list[i][1]).pack(side = BOTTOM)

    def show_map(self):
        self.heritage_map_url()
        self.Mwindow = Toplevel(bg = 'white')
        self.Mwindow.title(str(self.iid) + '번 결과 지도 정보')

        self.Mview = TkinterMapView(self.Mwindow, width=800, height=600, corner_radius=0)
        self.Mview.pack(fill="both", expand=True)
        self.Mview.set_position(self.lat, self.lng)
        self.Mview.set_zoom(self.zoom)

        self.Mmarker = self.Mview.set_marker(self.lat, self.lng, text = self.ccbaMnm1)
        self.Mview.add_right_click_menu_command(label = "Add Marker",
                                            command = self.add_marker_event,
                                            pass_coords=True)
        self.Mview.add_right_click_menu_command(label = "Connect Path to Marker",
                                            command = self.connect_path_event,
                                            pass_coords=True)

    def show_graph(self):
        self.Gwindow = Toplevel(bg = 'white')
        self.Gwindow.title('그래프 정보')
        self.Gwindow.geometry(str(self.Gcanvas_width + 100) + 'x' + str(self.Gcanvas_height + 50))

        self.Gframe1 = Frame(self.Gwindow, bg = 'white')
        self.Gframe1.pack(side = TOP, anchor = NW)

        self.Gframe2 = Frame(self.Gwindow, bg = 'white')
        self.Gframe2.pack(side = RIGHT)
        self.Gframe3 = Frame(self.Gwindow, bg = 'white')
        self.Gframe3.pack(side = LEFT)

        self.status = Label(self.Gframe1, text = '종목코드 별 분류 (page 1)', font = self.fontstyle1, bg = 'white')
        self.status.grid(row = 0, column = 0, padx = (100,0))
        Button(self.Gframe2, text = '>', command = self.Next, font = self.fontstyle1, bg = 'white', width = 3, height = 1).pack(padx = 10)
        Button(self.Gframe3, text = '<', command = self.Back, font = self.fontstyle1, bg = 'white', width = 3, height = 1).pack(padx = 10)

        self.Gcanvas1 = Canvas(self.Gwindow, bg = 'white', width = self.Gcanvas_width, height = self.Gcanvas_height - 50,
                            highlightbackground="black")
        self.Gcanvas1.pack()
        self.Gcanvas1.delete('all')

        self.Gcanvas2 = Canvas(self.Gwindow, bg = 'white', width = self.Gcanvas_width, height = 50,
                            highlightbackground="black")
        self.Gcanvas2.pack()
        self.Gcanvas2.delete('all')

        self.Gcanvas3 = Canvas(self.Gwindow, bg='white', width=self.Gcanvas_width, height=self.Gcanvas_height,
                            highlightbackground="black")
        self.Gcanvas3.pack_forget()
        self.Gcanvas3.delete('all')

        self.btnCnt = 0
        self.draw_canvas(self.btnCnt)

    def show_content(self):
        self.heritage_content_url()
        self.Cwindow = Toplevel(bg = 'white')
        self.Cwindow.title(str(self.iid) + '번 결과 문화재 정보')

        self.Ccanvas1 = Canvas(self.Cwindow, bg = 'white', width = self.Ccanvas_width, height = self.Ccanvas_height // 2)
        self.Ccanvas1.pack()

        with urllib.request.urlopen(self.CimageUrl) as u:
            raw_data = u.read()
        im = Image.open(io.BytesIO(raw_data))
        resized_image = im.resize((300, 300), Image.LANCZOS)
        self.Cphoto = ImageTk.PhotoImage(resized_image)
        self.Cimage_id = self.Ccanvas1.create_image(self.Ccanvas_width // 2, 150, image=self.Cphoto)

        self.Cframe = Frame(self.Cwindow, bg = 'white')
        self.Cframe.pack(side = BOTTOM)

        self.Ccanvas2 = Canvas(self.Cframe, bg = 'white', width = self.Ccanvas_width, height = self.Ccanvas_height // 2)
        self.Ccanvas2.pack()

        scrollbar = Scrollbar(self.Cframe, orient="vertical", command = self.Ccanvas2.yview)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")
        self.Ccanvas2.config(yscrollcommand = scrollbar.set)
        self.Ccanvas2.bind("<Configure>", self.on_canvas_configure)

        string = [word for word in self.Ccontent.split('\n')]
        result = []
        for item in string:
            if len(item) // 50 > 0:
                splits = [item[i:i + 50] for i in range(0, len(item), 50)]
                result += splits
            else:
                result.append(item)

        for i in range(len(result)):
            self.Ccanvas2.create_text(20, 20 + i * 20, anchor = 'w', text = result[i], font = self.fontstyle2, fill="black")

    def show_telegram(self):
        self.Twindow = Toplevel(bg = 'white')
        self.Twindow.title(str(self.iid) + '번 텔레그램 정보창')
        self.Twindow.geometry('600x100')

        self.Tframe = Frame(self.Twindow, bg = 'white')
        self.Tframe.pack(expand = True)

        Button(self.Tframe, text = '정보 확인', bg='white', font=self.fontstyle2, command=self.Reply,
               highlightbackground="blue", bd=1, relief="solid", width = 15, height = 3).pack(side = LEFT, padx = 10)
        Button(self.Tframe, text = '정보 저장', bg='white', font=self.fontstyle2, command=self.Save,
               highlightbackground="blue", bd=1, relief="solid", width = 15, height = 3).pack(side = LEFT, padx = 10)
        Button(self.Tframe, text = '저장 초기화', bg='white', font=self.fontstyle2, command=self.Clear,
               highlightbackground="blue", bd=1, relief="solid", width = 15, height = 3).pack(side = LEFT, padx = 10)
        Button(self.Tframe, text = '저장 확인', bg='white', font=self.fontstyle2, command=self.Check,
               highlightbackground="blue", bd=1, relief="solid", width = 15, height = 3).pack(side = LEFT, padx = 10)

    def show_txt(self):
        window = Toplevel(bg = 'white')
        window.title( 'txt 파일 정보창')
        window.geometry('450x100')

        frame = Frame(window, bg = 'white')
        frame.pack(expand = True)

        Button(frame, text = '파일 열기', bg='white', font=self.fontstyle2, command=self.OpenFile,
               highlightbackground="blue", bd=1, relief="solid", width = 15, height = 3).pack(side = LEFT, padx = 10)
        Button(frame, text = str(self.iid) + '번 저장', bg='white', font=self.fontstyle2, command=self.SaveFile,
               highlightbackground="blue", bd=1, relief="solid", width = 15, height = 3).pack(side = LEFT, padx = 10)
        Button(frame, text = '파일 초기화', bg='white', font=self.fontstyle2, command=self.ClearFile,
               highlightbackground="blue", bd=1, relief="solid", width = 15, height = 3).pack(side = LEFT, padx = 10)

    # buttons ---------------------------------------------------------------------------------------

    def Find(self):
        self.cnt = 1

        self.heritage_list.delete(*self.heritage_list.get_children())
        for heritage in self.HeritageTotalList:
            if self.PARAM.get() in heritage[self.select_type()]:
                item = (str(self.cnt), heritage['type'], heritage['CtcdNm'], heritage['siName'], heritage['name'],\
                    heritage['ccbaAdmin'], heritage['ccbaKdcd'], heritage['ccbaCtcd'], heritage['ccbaAsno'])
                self.heritage_list.insert("", END, values = item, iid = str(self.cnt))
                self.cnt += 1
        self.label.configure(text = 'Total : ' + str(self.cnt - 1))

    def Origin(self):
        self.heritage_list.delete(*self.heritage_list.get_children())
        self.show_heritage()
        self.label.configure(text = 'Total : ' + str(self.cnt))

    def Next(self):
        if self.btnCnt < 2:
            self.btnCnt += 1
            self.draw_canvas(self.btnCnt)

    def Back(self):
        if self.btnCnt > 0:
            self.btnCnt -= 1
            self.draw_canvas(self.btnCnt)

    def Reply(self):
        text = '정보확인'
        self.handle_teller(text)

    def Save(self):
        text = '정보저장'
        self.handle_teller(text)

    def Clear(self):
        text = '저장초기화'
        self.handle_teller(text)

    def Check(self):
        text = '저장확인'
        self.handle_teller(text)

    def OpenFile(self):
        window = Toplevel()
        window.withdraw()
        file_path = filedialog.askopenfilename()
        t = threading.Thread(target = spam.open, args=(file_path,))
        t.start()

    def SaveFile(self):
        index = int(self.item)
        ccbakdcd = self.HeritageTotalList[index]['ccbaKdcd']
        ccbaasno = self.HeritageTotalList[index]['ccbaAsno']
        ccbactcd = self.HeritageTotalList[index]['ccbaCtcd']

        url = 'http://www.cha.go.kr/cha/SearchKindOpenapiDt.do?ccbaKdcd=' + ccbakdcd + '&ccbaAsno=' + ccbaasno + '&ccbaCtcd=' + ccbactcd
        response = requests.get(url)
        root = ET.fromstring(response.text)
        ccbaMnm1 = root.findtext(".//item//ccbaMnm1")
        content = root.findtext(".//item//content")

        spam.save('save.txt', ccbaMnm1)
        spam.save('save.txt', content)

        window = Toplevel(bg='white')
        window.title(str(self.iid) + '번 txt 저장')
        window.geometry('250x100')

        frame = Frame(window, bg='white')
        frame.pack(expand=True)

        Label(frame, text='저장을 완료하였습니다.', font=self.fontstyle1, bg='white').pack()
        
    def ClearFile(self):
        spam.clear('save.txt')

        window = Toplevel(bg='white')
        window.title('txt 초기화')
        window.geometry('250x100')

        frame = Frame(window, bg='white')
        frame.pack(expand=True)

        Label(frame, text='초기화를 완료하였습니다.', font=self.fontstyle1, bg='white').pack()

    # -----------------------------------------------------------------------------------------------
    def add_marker_event(self, coords):
        self.markercnt += 1
        new_marker = self.Mview.set_marker(coords[0], coords[1], text= 'New ' + str(self.markercnt))

    def connect_path_event(self, coords):
        self.markercnt += 1
        new_marker = self.Mview.set_marker(coords[0], coords[1], text= 'New ' + str(self.markercnt))
        path_1 = self.Mview.set_path([self.Mmarker.position, new_marker.position])

    def handle_teller(self, text):
        index = int(self.item)
        ccbakdcd = self.HeritageTotalList[index - 1]['ccbaKdcd']
        ccbaasno = self.HeritageTotalList[index - 1]['ccbaAsno']
        ccbactcd = self.HeritageTotalList[index - 1]['ccbaCtcd']

        self.Turl = 'http://www.cha.go.kr/cha/SearchKindOpenapiDt.do?ccbaKdcd=' + ccbakdcd + '&ccbaAsno=' + ccbaasno + '&ccbaCtcd=' + ccbactcd
        self.Tresponse = requests.get(self.Turl)
        self.Troot = ET.fromstring(self.Tresponse.text)
        self.TccbaMnm1 = self.Troot.findtext(".//item//ccbaMnm1")
        self.Tcontent = self.Troot.findtext(".//item//content")

        teller.ccbakdcd, teller.ccbaasno, teller.ccbactcd = ccbakdcd, ccbaasno, ccbactcd
        teller.text = text
        teller.handle(teller.text, self.TccbaMnm1 + '\n\n' + self.Tcontent)
        if(teller.handle):
            window = Toplevel(bg = 'white')
            window.title(str(self.iid) + '번 ' + text)
            window.geometry('250x100')

            frame = Frame(window, bg = 'white')
            frame.pack(expand = True)

            Label(frame, text = '요청을 완료하였습니다.', font = self.fontstyle1, bg = 'white').pack()
    
    def on_canvas_configure(self, event):
        self.Ccanvas2.configure(scrollregion = self.Ccanvas2.bbox("all"))

    def draw_canvas(self, cnt):
        category = [11, 12, 13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 31, 79, 80]
        result = [357, 2432, 582, 10, 134, 594, 163, 318, 4605, 680, 2093, 538, 74, 3218, 970, 21]
        total = 16789

        self.value = 16
        self.subvalue = self.value // 2
        self.barWidth = (self.Gcanvas_width - self.subvalue) / self.subvalue

        if cnt == 0:
            self.Gcanvas1.pack()
            self.Gcanvas2.pack()
            self.Gcanvas3.pack_forget()
            self.status.configure(text = '종목코드 별 분류 (page 1)')
            self.Gcanvas1.delete('histogram')
            for i in range(self.subvalue):
                self.Gcanvas1.create_rectangle(25 + i * self.barWidth, self.Gcanvas_height - (result[i] / total) * 400 - 300,
                                               25 + i * self.barWidth + 20, self.Gcanvas_height, fill='red', tags='histogram')
                self.Gcanvas1.create_text(25 + i * self.barWidth + 10, self.Gcanvas_height - (result[i] / total) * 400 - 310,
                                          text=str(result[i]), font=self.fontstyle1, tags='histogram')

            self.Gcanvas2.delete('text')
            for i in range(self.subvalue):
                self.Gcanvas2.create_text(25 + i * self.barWidth + 10, 25, text=str(category[i]), font=self.fontstyle1,
                                          tags='text')
        if cnt == 1:
            self.Gcanvas1.pack()
            self.Gcanvas2.pack()
            self.Gcanvas3.pack_forget()
            self.status.configure(text = '종목코드 별 분류 (page 2)')
            self.Gcanvas1.delete('histogram')
            for i in range(self.subvalue, self.value):
                self.Gcanvas1.create_rectangle(25 + (i - self.subvalue) * self.barWidth, self.Gcanvas_height - (result[i] / total) * 400 - 300,
                                               25 + (i - self.subvalue) * self.barWidth + 20, self.Gcanvas_height, fill='red', tags='histogram')
                self.Gcanvas1.create_text(25 + (i - self.subvalue) * self.barWidth + 10, self.Gcanvas_height - (result[i] / total) * 400 - 310,
                                          text=str(result[i]), font=self.fontstyle1, tags='histogram')

            self.Gcanvas2.delete('text')
            for i in range(self.subvalue, self.value):
                self.Gcanvas2.create_text(25 + (i - self.subvalue) * self.barWidth + 10, 25, text=str(category[i]), font=self.fontstyle1,
                                          tags='text')
        if cnt == 2:
            self.Gcanvas1.pack_forget()
            self.Gcanvas2.pack_forget()
            self.Gcanvas3.pack()
            self.status.configure(text = '종목코드 별 분류 (page 3)(끝)')

            start = 0

            for i in range(self.value):
                extent = result[i] / total * 360
                color = self.random_color()
                self.Gcanvas3.create_arc((150, 50, 650, 550), fill = color, outline='white', start = start, extent = extent)
                start = start + extent
                self.Gcanvas3.create_rectangle(700, 20 + 20 * i, 700 + 30, 20 + 20 * (i + 1), fill = color)
                self.Gcanvas3.create_text(700 + 50, 10 + 20 * (i + 1), text=str(category[i]))

    def random_color(self):
        color = '#'
        colors = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        for i in range(6):
            color += colors[random.randint(0, 15)]
        return color

    def showMap(self, frame):
        global browser
        sys.excepthook = cef.ExceptHook
        window_info = cef.WindowInfo(frame.winfo_id())
        window_info.SetAsChild(frame.winfo_id(), [0, 0, 800, 600])
        cef.Initialize()
        browser = cef.CreateBrowserSync(window_info, url='file:///map.html')
        cef.MessageLoop()

    def show_heritage(self):
        self.cnt = 1
        for heritage in self.HeritageTotalList:
            item = (str(self.cnt), heritage['type'], heritage['CtcdNm'], heritage['siName'], heritage['name'],\
                    heritage['ccbaAdmin'], heritage['ccbaKdcd'], heritage['ccbaCtcd'], heritage['ccbaAsno'])
            self.heritage_list.insert("", END, values = item, iid = str(self.cnt))
            self.cnt += 1

    def select_type(self):
        if self.TYPE.get() == self.TYPE_list[1]:
            return 'type'
        if self.TYPE.get() == self.TYPE_list[2]:
            return 'CtcdNm'
        if self.TYPE.get() == self.TYPE_list[3]:
            return 'siName'
        if self.TYPE.get() == self.TYPE_list[4]:
            return 'name'
        if self.TYPE.get() == self.TYPE_list[5]:
            return 'ccbaAdmin'
        if self.TYPE.get() == self.TYPE_list[6]:
            return 'ccbaKdcd'
        if self.TYPE.get() == self.TYPE_list[7]:
            return 'ccbaCtcd'
        if self.TYPE.get() == self.TYPE_list[8]:
            return 'ccbaAsno'

    def popup_menu(self, event):
        # 항목 선택
        self.item = self.heritage_list.identify_row(event.y)
        if self.item:
            self.heritage_list.selection_set(self.item)  # 항목 선택 설정

            selected_items = self.heritage_list.selection()
            self.iid = selected_items[0]

            # 컨텍스트 메뉴 생성
            self.menu = Menu(self.heritage_list, tearoff=0)
            self.menu.add_command(label = "지도", command = self.show_map)
            self.menu.add_command(label = "이미지", command = self.show_image)
            self.menu.add_command(label = "정보", command = self.show_content)
            self.menu.add_command(label = "텔레그램", command = self.show_telegram)
            self.menu.add_command(label = "txt 파일", command = self.show_txt)

            # 이벤트 위치에 컨텍스트 메뉴 표시
            self.menu.post(event.x_root, event.y_root)

    def __init__(self):
        self.set_heritage()

        self.width, self.height = 1350, 640
        self.Mcanvas_width, self.Mcanvas_height = 800, 600
        self.Gcanvas_width, self.Gcanvas_height = 800, 600
        self.Ccanvas_width,self.Ccanvas_height = 650, 600

# -------------------------------------------------------------------------------------------------

        self.window = Tk()
        self.window.title('문화재 검색 프로그램')
        self.window.configure(bg = 'white')
        self.window.geometry(str(self.width) + 'x' + str(self.height))

        self.fontstyle1 = tkinter.font.Font(family = 'Consolas', size = 12, weight = 'bold')
        self.fontstyle2 = tkinter.font.Font(family = 'Consolas', size = 10, weight = 'bold')
        self.fontstyle3 = tkinter.font.Font(family = 'Consolas', size = 8, weight = 'bold')
        self.style = ttk.Style()
        self.font=('Consolas', 8, 'bold')

# frame1 ------------------------------------------------------------------------------------------

        self.frame1 = Frame(self.window, bg = 'white')
        self.frame1.pack(side = TOP, anchor = CENTER)

        self.TYPE_list = ['번호', '문화재종목', '시도명', '시군구명', '문화재명', '관리자', '종목코드', '시도코드', '관리번호']
        self.TYPE = StringVar()
        self.TYPE.set('문화재명')
        self.combobox = ttk.Combobox(self.frame1, textvariable = self.TYPE, font = self.fontstyle3, values = self.TYPE_list, width = 10)
        self.combobox.grid(row = 0, column = 0)

        self.PARAM = StringVar()
        Entry(self.frame1, textvariable = self.PARAM, font = self.fontstyle3,\
              justify = LEFT, width = 50, bg = 'light gray').grid(pady = 10, row = 0, column = 1)
        Button(self.frame1, text = '검색', font = self.fontstyle3, command = self.Find, bg = 'white').grid(row = 0, column = 2, sticky = E)

# frame2 -------------------------------------------------------------------------------------------

        self.frame2 = Frame(self.window, bg = 'white')
        self.frame2.pack(side = BOTTOM, anchor = SW)

        for item in self.root.iter('result'):
            self.list_total_count = item.findtext("totalCnt")
            self.label = Label(self.frame2, text = 'Total : ' + self.list_total_count, font = self.fontstyle1, bg = 'white')
            self.label.grid(row = 0)

# frame3 -------------------------------------------------------------------------------------------

        self.frame3 = Frame(self.window, width = 1000, bg = 'white')
        self.frame3.pack(side = TOP, anchor = NW)

        self.guide = Label(self.frame3, text = '우클릭으로 더보기', font = self.fontstyle2, bg = 'white')
        self.guide.grid(row=0, column=0, padx=(0, 1105))

        self.graph = Button(self.frame3, text = '통계', bg = 'white', font = self.fontstyle2, command = self.show_graph, highlightbackground="black", bd=1, relief="solid")
        self.graph.grid(row=0, column=2, padx=(0, 5))
        self.origin = Button(self.frame3, text = '전체보기', bg = 'white', font = self.fontstyle2, command = self.Origin, highlightbackground="black", bd=1, relief="solid")
        self.origin.grid(row=0, column=3)

# Treeview  ----------------------------------------------------------------------------------------
        self.width_list = [50, 120, 70, 70, 450, 320, 70, 70, 100]

    # 정렬값 출력
        self.heritage_list = ttk.Treeview(self.window, show = 'headings')
        self.heritage_list.pack(side = LEFT, fill = BOTH)

        self.heritage_list["columns"] = tuple(self.TYPE_list)
        for i in range(len(self.TYPE_list)):
            self.heritage_list.column(self.TYPE_list[i], width = self.width_list[i])
        # 열 제목 설정
        for i in range(len(self.TYPE_list)):
            self.heritage_list.heading(self.TYPE_list[i], text = self.TYPE_list[i])

        self.scrollbar = Scrollbar(self.window)
        self.scrollbar.pack(side = LEFT, fill = Y)
        self.heritage_list.config(yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.heritage_list.yview)

        self.show_heritage()

# right click ---------------------------------------------------------------------------------------

        self.heritage_list.bind("<Button-3>", self.popup_menu)
        self.window.mainloop()

# ---------------------------------------------------------------------------------------------------
MainGUI()
# 지도, 이미지, 그래프, 검색 무조건 넣을것