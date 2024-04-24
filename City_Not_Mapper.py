import folium, io, json, sys, math, random, os
import psycopg2
from folium.plugins import Draw, MousePosition, MeasureControl
from jinja2 import Template
from branca.element import Element
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        

        self.resize(600, 600)
        with open('config.json') as config_file:
            self.config = json.load(config_file)
        main = QWidget()
        self.setCentralWidget(main)
        main.setLayout(QVBoxLayout())
        main.setFocusPolicy(Qt.StrongFocus)

        self.tableWidget = QTableWidget()
        self.tableWidget.doubleClicked.connect(self.table_Click)
        self.rows = []

        self.webView = myWebView()
		
        controls_panel = QHBoxLayout()
        mysplit = QSplitter(Qt.Vertical)
        mysplit.addWidget(self.tableWidget)
        mysplit.addWidget(self.webView)

        main.layout().addLayout(controls_panel)
        main.layout().addWidget(mysplit)

        _label = QLabel('From: ', self)
        _label.setFixedSize(30,20)
        self.from_box = QComboBox() 
        self.from_box.setEditable(True)
        self.from_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.from_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.from_box)

        _label = QLabel('  To: ', self)
        _label.setFixedSize(20,20)
        self.to_box = QComboBox() 
        self.to_box.setEditable(True)
        self.to_box.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.to_box.setInsertPolicy(QComboBox.NoInsert)
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.to_box)

        _label = QLabel('Hops: ', self)
        _label.setFixedSize(20,20)
        self.hop_box = QComboBox() 
        self.hop_box.addItems( ['1', '2', '3', '4', '5'] )
        self.hop_box.setCurrentIndex( 2 )
        controls_panel.addWidget(_label)
        controls_panel.addWidget(self.hop_box)

        self.transport_box = QComboBox()
        self.transport_box.addItems(["Tout", "Train", "Metro", "Bus", "Tram"])
        controls_panel.addWidget(self.transport_box)

        self.go_button = QPushButton("Go!")
        self.go_button.clicked.connect(self.button_Go)
        controls_panel.addWidget(self.go_button)
           
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.button_Clear)
        controls_panel.addWidget(self.clear_button)

        self.maptype_box = QComboBox()
        self.maptype_box.addItems(self.webView.maptypes)
        self.maptype_box.currentIndexChanged.connect(self.webView.setMap)
        controls_panel.addWidget(self.maptype_box)

        self.cityComboBox = QComboBox()
        self.cityComboBox.addItems([city['name'] for city in self.config['cities']])
        controls_panel.addWidget(self.cityComboBox)
        self.cityComboBox.currentIndexChanged.connect(self.updateCity)

        self.initUI()
        self.connect_DB()

        self.startingpoint = True
                   
        self.show()

    def updateCity(self):
        selected_city = self.cityComboBox.currentText()
        self.connect_DB(selected_city)
        self.webView.clearMap(0)
        self.startingpoint = True
        self.update()

    def initUI(self):
        self.resize(800, 800) 
        self.setWindowTitle("City Not Mapper")  

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                border: 2px solid #8f8f8f;
                border-radius: 6px;
                background-color: #e7e7e7;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d7d7d7;
            }
            QTableWidget {
                border: 1px solid #dddddd;
            }
            QComboBox {
                border: 1px solid gray;
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:editable {
                background: white;
            }
        """)


    def connect_DB(self, selected_city=None):
        if selected_city is None:
        
            selected_city = self.cityComboBox.currentText()
    
        selected_city = self.cityComboBox.currentText()

        for city in self.config['cities']:
            if city['name'] == selected_city:
                database = city['database']
                user = city['user']
                host = city['host']
                password = city['password']
                tables = city['tables']

                conn = psycopg2.connect(database=database, user=user, host=host, password=password)
                cursor = conn.cursor()

                for table in tables:
                    cursor.execute(f"SELECT distinct stop_name FROM {table} ORDER BY stop_name")
                    conn.commit()
                    rows = cursor.fetchall()

                    for row in rows:
                        self.from_box.addItem(str(row[0]))
                        self.to_box.addItem(str(row[0]))

                
                self.conn = conn
                self.cursor = cursor


    def table_Click(self):
        k = 0
        prev_lat = 0
        for col in self.rows[self.tableWidget.currentRow()] :
            if (k % 3) == 0:
                lst = col.split(',')
                lon = float(lst[0])
                lat = float(lst[1])
                if prev_lat != 0:
                    self.webView.addSegment( prev_lat, prev_lon, lat, lon )
                prev_lat = lat
                print(prev_lat)
                prev_lon = lon
                self.webView.addMarker( lat, lon )
            k = k + 1

  
    def button_Go(self):
        selected_city = self.cityComboBox.currentText()
        center_coordinates = [city['coordinates'] for city in self.config['cities'] if city['name'] == selected_city][0]
        self.tableWidget.clearContents()

        _fromstation = str(self.from_box.currentText())
        _tostation = str(self.to_box.currentText())
        _hops = int(self.hop_box.currentText())
        _transport = str(self.transport_box.currentText())
        

        if  _transport == "Tout" :
            _transport = "0"
            _transport1 = "1"
            _transport2 = "2"
            _transport3 = "3"

        if  _transport == "Bus" :
            _transport = "3"
            _transport1 = "99"
            _transport2 = "99"
            _transport3 = "99"

        if  _transport == "Train" :
            _transport = "2"
            _transport1 = "99"
            _transport2 = "99"
            _transport3 = "99"

        if  _transport == "Metro" :
            _transport = "1"
            _transport1 = "99"
            _transport2 = "99"
            _transport3 = "99"

        if  _transport == "Tram" :
            _transport = "0"
            _transport1 = "99"
            _transport2 = "99"
            _transport3 = "99"
        
        self.rows = []
        table_name = f"stop_route_info_{selected_city.lower()}"

        if _hops >= 1 : 
            self.cursor.execute(""f"SELECT DISTINCT A.coordinates_text, A.stop_name, A.route_name, B.coordinates_text, B.stop_name FROM {table_name} as A, {table_name} as B WHERE A.stop_name = $${_fromstation}$$ AND B.stop_name = $${_tostation}$$ AND A.route_name = B.route_name AND A.route_type IN ($${_transport}$$,$${_transport1}$$,$${_transport2}$$,$${_transport3}$$) """)
            self.conn.commit()
            self.rows += self.cursor.fetchall()
            
            
            
        if _hops >= 2 : 
            self.cursor.execute(""f"SELECT DISTINCT A.coordinates_text, A.stop_name, A.route_name, B.coordinates_text, B.stop_name, C.route_name, D.coordinates_text, D.stop_name FROM {table_name} as A, {table_name} as B, {table_name} as C, {table_name} as D WHERE A.stop_name = $${_fromstation}$$ AND D.stop_name = $${_tostation}$$ AND A.route_name = B.route_name AND B.stop_name = C.stop_name AND C.route_name = D.route_name AND A.route_type IN ($${_transport}$$,$${_transport1}$$,$${_transport2}$$,$${_transport3}$$) AND A.route_type = C.route_type AND A.route_name <> C.route_name AND A.stop_name <> B.stop_name AND B.stop_name <> D.stop_name LIMIT 10""")
            self.conn.commit()
            self.rows += self.cursor.fetchall()

        if _hops >= 3 : 
            self.cursor.execute(""f"SELECT DISTINCT A.coordinates_text, A.stop_name, A.route_name, B2.coordinates_text, B2.stop_name, B2.route_name, C2.coordinates_text, C2.stop_name, C2.route_name, D.coordinates_text, D.stop_name FROM {table_name} as A, {table_name} as B1, {table_name} as B2, {table_name} as C1, {table_name} as C2, {table_name} as D WHERE A.stop_name = $${_fromstation}$$ AND A.route_name = B1.route_name AND B1.stop_name = B2.stop_name AND B2.route_name = C1.route_name AND C1.stop_name = C2.stop_name AND C2.route_name = D.route_name AND D.stop_name = $${_tostation}$$ AND A.route_type IN ($${_transport}$$,$${_transport1}$$,$${_transport2}$$,$${_transport3}$$) AND A.route_type = C1.route_type AND A.route_type = D.route_type AND A.route_name <> B2.route_name AND B2.route_name <> C2.route_name AND A.route_name <> C2.route_name AND A.stop_name <> B1.stop_name AND B2.stop_name <> C1.stop_name AND C2.stop_name <> D.stop_name LIMIT 10""")
            self.conn.commit()
            self.rows += self.cursor.fetchall()
    
        if len(self.rows) == 0 : 
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(0)
            self.webView.setMap(0, center_coordinates, 12)
            return
        
        numrows = len(self.rows)
        numcols = len(self.rows[-1]) - math.floor(len(self.rows[-1]) / 3.0) - 1 
        self.tableWidget.setRowCount(numrows)
        self.tableWidget.setColumnCount(numcols)
        print(self.rows)
        i = 0
        for row in self.rows : 
            j = 0
            k = 0 
            for col in row :
                if j % 3 == 0 : 
                    k = k + 1
                else : 
                    self.tableWidget.setItem(i, j-k, QTableWidgetItem(str(col)))
                j = j + 1
            i = i + 1

        header = self.tableWidget.horizontalHeader()
        j = 0
        while j < numcols : 
            header.setSectionResizeMode(j, QHeaderView.ResizeToContents)
            j = j+1
        self.update()	

    def button_Clear(self):
        self.webView.clearMap(self.maptype_box.currentIndex())
        self.startingpoint = True
        self.update()


    def mouseClick(self, lat, lng):
        self.webView.addPointMarker(lat, lng)
        selected_city = self.cityComboBox.currentText()
        table_name = f"stop_route_info_{selected_city.lower()}"
        print(f"Clicked on: latitude {lat}, longitude {lng}")
        self.cursor.execute(f"""
    WITH mytable (distance, name) AS (
        SELECT ABS(lat - {lat}) + ABS(lon - {lng}), stop_name
        FROM {table_name}
    )
    SELECT A.name
    FROM mytable A
    WHERE A.distance <= (SELECT MIN(B.distance) FROM mytable B)
""")

        self.conn.commit()
        rows = self.cursor.fetchall()
       
        if self.startingpoint :
            self.from_box.setCurrentIndex(self.from_box.findText(rows[0][0], Qt.MatchFixedString))
        else :
            self.to_box.setCurrentIndex(self.to_box.findText(rows[0][0], Qt.MatchFixedString))
        self.startingpoint = not self.startingpoint



class myWebView (QWebEngineView):
    def __init__(self):
        super().__init__()
        
        self.maptypes = ["OpenStreetMap", "Stamen Terrain", "stamentoner", "cartodbpositron"]
        self.setMap(0)


    def add_customjs(self, map_object):
        my_js = f"""{map_object.get_name()}.on("click",
                 function (e) {{
                    var data = `{{"coordinates": ${{JSON.stringify(e.latlng)}}}}`;
                    console.log(data)}}); """
        e = Element(my_js)
        html = map_object.get_root()
        html.script.get_root().render()
        html.script._children[e.get_name()] = e

        return map_object


    def handleClick(self, msg):
        data = json.loads(msg)
        lat = data['coordinates']['lat']
        lng = data['coordinates']['lng']


        window.mouseClick(lat, lng)


    def addSegment(self, lat1, lng1, lat2, lng2):
        js = Template(
        """
        L.polyline(
            [ [{{latitude1}}, {{longitude1}}], [{{latitude2}}, {{longitude2}}] ], {
                "color": "red",
                "opacity": 1.0,
                "weight": 4,
                "line_cap": "butt"
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude1=lat1, longitude1=lng1, latitude2=lat2, longitude2=lng2 )

        self.page().runJavaScript(js)


    def addMarker(self, lat, lng):
        js = Template(
        """
        L.marker([{{latitude}}, {{longitude}}] ).addTo({{map}});
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": "#3388ff",
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "#3388ff",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def addPointMarker(self, lat, lng):
        js = Template(
        """
        L.circleMarker(
            [{{latitude}}, {{longitude}}], {
                "bubblingMouseEvents": true,
                "color": 'green',
                "popup": "hello",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": 'green',
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "opacity": 1.0,
                "radius": 2,
                "stroke": true,
                "weight": 5
            }
        ).addTo({{map}});
        """
        ).render(map=self.mymap.get_name(), latitude=lat, longitude=lng)
        self.page().runJavaScript(js)


    def setMap(self, i, center_coordinates=None, zoom=None):
        center_coordinates = center_coordinates or [48.8619266629, 2.3519030802]
        zoom = zoom or 12
        self.mymap = folium.Map(location=center_coordinates, tiles=self.maptypes[i], zoom_start=zoom, prefer_canvas=True)
        self.mymap = self.add_customjs(self.mymap)
        page = WebEnginePage(self)
        self.setPage(page)
        data = io.BytesIO()
        self.mymap.save(data, close_file=False)
        self.setHtml(data.getvalue().decode())

    def clearMap(self, index):
        self.setMap(index)



class WebEnginePage(QWebEnginePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        #print(msg)
        if 'coordinates' in msg:
            self.parent.handleClick(msg)


       
			
if __name__ == '__main__':
    sys.argv.append('--no-sandbox')
    app = QApplication(sys.argv) 
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
