try:
    from PySide6.QtWidgets import QMainWindow, QApplication
    from PySide6.QtWidgets import QListWidget, QLineEdit, QSpinBox
    from PySide6.QtWidgets import QPushButton, QHeaderView, QTableWidgetItem
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import Qt, QFile, Slot
    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QMenu
    from PySide6.QtGui import QAction,QCursor
except:
    from PySide2.QtWidgets import QMainWindow, QApplication
    from PySide2.QtWidgets import QListWidget, QLineEdit, QSpinBox
    from PySide2.QtWidgets import QHBoxLayout, QLabel, QWidget
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import Qt, QFile   
    import maya.cmds as cmds 
import os
import shutil   # 모듈 불러오기


class Loader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()

        # 최초의 경로를 받아온다.
        self.root_path = "/nas/show" #내가 시작하는 최초의 경로를 불러온다.
        
        self.ui.comboBox_project.addItems(self.get_projects()) # 콤보박스 
        self.ui.listWidget_category.addItems(self.get_asset_category()) # 1번째 위젯
        self.ui.listWidget_category.currentItemChanged.connect(self.get_asset) #signal은 ()를 사용하지 않는다.
        self.ui.tableWidget_asset.cellClicked.connect(self.get_task) # 2번째 위젯
        self.ui.listWidget_tasks.currentItemChanged.connect(self.get_scenes) # 3번째 위젯

        # 우클릭시 뜨게하기
        self.table = self.ui.tableWidget_asset # 2번째 위젯은 table이다.
        self.table.setContextMenuPolicy(Qt.CustomContextMenu) # 우클릭시 뜨게하는 함수
        self.table.customContextMenuRequested.connect(self.show_context_menu) # 우클릭시 뜨는 메서드


    # 마우스 우클릭시 불러오는 메서드
    def show_context_menu(self):
        self.table_menu = QMenu() # 변수명(self.table_menu)은 QMenu()이다.
        menu1 = self.table_menu.addAction("add asset") # self.table_menu에 add asset라는 것을 추가

        # 각 메뉴별로 메소드 연결
        menu1.triggered.connect(self.show_input_window) # add asset을 누르면 self.show_input_window메서드로 연결

        pos = QCursor.pos() # 마우스 커서의 위치값
        self.table_menu.move(pos) # 메뉴를 지정된 위치로 이동시키는 역할
        self.table_menu.show() # table_menu인 QMenu를 보여준다.

    def show_input_window(self): # add asset 클릭시 연결되는 메서드
        self.sub_load_ui() # sub_ui 로드
        self.sub_ui.pushButton.clicked.connect(self.add_asset_to_table) # ui의 버튼 클릭시 메서드 연결

    def add_asset_to_table(self): # ui 버튼 클릭시 실행되는 메서드
        name = self.sub_ui.lineEdit.text()  # lineEdit에서 에셋 제목 텍스트 받아오기
        sum_pic = self.sub_ui.lineEdit_sum.text() # lineEdit에서 에셋 경로 텍스트 받아오기
        if not name:  # 이름이 비어있으면 반환
            return
        # 이미지 경로가 존재하는지 확인
        if not os.path.exists(sum_pic):
            print("이미지가 존재하지 않습니다.")
            return

        # 폴더 경로를 생성 (name으로 폴더 이름 설정)
        asset_folder = f"/nas/show/academy/assets/char/{name}"

        if not os.path.exists(asset_folder): # 정의한 경로에 폴더 생성
            os.makedirs(asset_folder)  # 폴더가 없으면 생성

        # 이미지 파일 이름을 'thumb.jpg'로 변경하여 저장할 경로 설정
        thumb_path = os.path.join(asset_folder, "thumb.jpg") # thumb_path는 asset_folder경로에 thumb.jpg이름을 가진다.

        try: #sum_pic에서 적은 텍스트를 thumb_path를 복사한다.
            shutil.copy(sum_pic, thumb_path)  # 이미지를 thumb.jpg로 복사
        except Exception as e: # 실패시
            print(f"이미지 복사 실패: {e}")
            return

        # 이미지 복사된 경로로 업데이트
        sum_pic = thumb_path # sum_pic은 thumb_path의 정보를 가진다.

        row = self.ui.tableWidget_asset.rowCount()  # 현재 테이블에 있는 행 수를 기반으로 추가할 행 번호 계산

        # 테이블에 새로운 행을 추가
        self.ui.tableWidget_asset.insertRow(row) # 2번째 위젯에 내용 추가

        # 새로 추가할 셀에 위젯을 삽입
        self.make_sub_asset(name, row, sum_pic) # 위젯 생성 - 삽입 메서드

    def make_sub_asset(self, name, row, sum_pic):
        # 위젯 생성
        widget = QWidget()  # QWidget 생성
        hbox_layout = QHBoxLayout()  # 수평 레이아웃 생성
        text_label = QLabel()  # 텍스트 라벨 생성
        text_label.setText(name)  # 라벨에 이름 설정/이름은 lineEdit.text에서 작성한 이름이다.
        text_label.setObjectName("label_asset_name")  # 라벨에 objectName 설정

        image_label = QLabel()  # 이미지를 넣을 라벨 생성
        image_label.setObjectName("label_image")

        pic_path = f"{sum_pic}" # 사진의 경로는 thumb_path의 정보를 가진 sum_pic
        pixmap = QPixmap(pic_path) # pixmap은 pic_path의 경로를 가진다
        scaled_pixmap = pixmap.scaled(80, 80)  # 스케일 수정 후 scaled_pixmap변수에 담기
        image_label.setPixmap(scaled_pixmap)  # 라벨에 이미지 넣기

        # 레이아웃에 텍스트 라벨 추가
        hbox_layout.addWidget(text_label) # 레이아웃에 텍스트 추가
        hbox_layout.addWidget(image_label)  # 레이아웃에 이미지 추가
        widget.setLayout(hbox_layout)  # 위젯에 레이아웃 설정

        # tableWidget_asset의 새 행, 첫 번째 열에 위젯 삽입
        self.ui.tableWidget_scenes.setCellWidget(row, 0, widget)

# 파일 경로대로 불러오기
    def get_projects(self):
        projects = [] # 빈 리스트 선언

        for name in os.listdir(self.root_path): # name이 최초의 경로에 존재할때
            project_path = f"{self.root_path}/{name}" # 경로 만들기 
            if not os.path.isdir(project_path): # 디렉토리가 아니면
                continue
            projects.append(name) # 이름을 붙인다.
        return projects
    
    def get_asset_category(self): # 위의 메서드에서 내용을 addItems로 더해줌
        asset_cartagory = [] # 빈 리스트 선언
        project = self.ui.comboBox_project.currentText() # 프로젝트는 comboBox_project
        task_type_path = f"{self.root_path}/{project}/assets" # 경로는 최초의 경로/콤보박스 텍스트/assets이다.

        for category in os.listdir(task_type_path): # 정의한 경로
            category_path = f"{task_type_path}/{category}" # 위에 합친 경로 + 경로 만들기
            if not os.path.isdir(category_path): # 디렉토리가 아니면
                continue
            asset_cartagory.append(category) # 리스트에 내가 만든 경로 붙이기
        return asset_cartagory 
    
    def get_asset(self, item):
        """
        currentItemChanged시그널을 사용하면 클릭한 리스트 위젯의 아이템이 객체로 전달
        /nas/show/academy/assets/char 경로에 있는 파일들의 리스트 출력
        """
        project = self.ui.comboBox_project.currentText() # 
        asset_cartagory = item.text() # asset_cartagory는 item의 
        asset_path = f"/nas/show/{project}/assets/{asset_cartagory}"  # asset의 경로 지정

        assets = os.listdir(asset_path) # 지정한 경로를 가지게 한다.   
        assets_count = len(assets) # 현재 선택한 경로에서 에셋의 수를 변수에 담음

        # tableWidget_asset에 에셋의 수를만큼 행 만들기
        self.ui.tableWidget_asset.setRowCount(assets_count) # 에셋의 수만큼 생성
        self.ui.tableWidget_asset.setColumnCount(1) # 1칸으로 정의 

        for row, asset in enumerate(assets): # 나의 경로에 있는 에셋
            self.make_asset_table(asset, asset_path, row) # 메서드 불러오기 에셋, 에셋의 경로, 줄을 보냄
        
    def make_asset_table(self, asset, asset_path, row): # 위에서 생성된 에셋, 에셋의 경로, 줄을 가진다.
        # 생성하는 이름 정의
        widget = QWidget() # 위젯 생성
        hbox_layout = QHBoxLayout() # 수평레이아웃 생성
        image_label = QLabel() # 이미지를 넣을 라벨 생성
        image_label.setObjectName("label_image")
        text_label = QLabel() # 에셋의 이름을 작성할 라벨 생성
        text_label.setText(asset) # 텍스트 라벨에 에셋 이름 넣어주기
        text_label.setObjectName("label_asset_name")

        # 이미지 라벨에 그림 넣기
        thumb_path = f"{asset_path}/{asset}/thumb.jpg"
        pixmap = QPixmap(thumb_path)
        scaled_pixmap = pixmap.scaled(80, 80) # 스케일 수정 후 scaled_pixmap변수에 담기
        image_label.setPixmap(scaled_pixmap) # 라벨에 이미지 넣기

        hbox_layout.addWidget(image_label) # 레이아웃에 1번째 위젯을 추가
        hbox_layout.addWidget(text_label) # 레이아웃에 2번째 위젯을 추가

        widget.setLayout(hbox_layout) # 위젯에 레이아웃을 추가한다.
        self.ui.tableWidget_asset.setCellWidget(row, 0, widget) # 테이블 위젯 0, 0에 위젯을 삽입

    def get_task(self, row, col):
        """
        /nas/show/academy/assets/char/teapot
        """
        project = self.ui.comboBox_project.currentText()
        asset_type = self.ui.listWidget_category.currentItem().text() # 2번째 위젯에서 선택한 에셋의 타입

        widget = self.ui.tableWidget_asset.cellWidget(row, col) # make_table에서 만든 위젯의 행과 열을 반환받음
        childs = widget.children() # 위젯의 자식
        for child_widget in childs: # 2번째 위젯에서 만든 자식들
            if child_widget.objectName() == "label_asset_name": # 자식들의 이름 조건문(위에서 이름을 동일하게 설정했음)
                asset_name = child_widget.text() # 에셋의 이름을 위에서 생성된 이름으로
                break

        tasks = [] # 빈리스트
        task_dir = f"/nas/show/{project}/assets/{asset_type}" # 추가된 경로
        items = os.listdir(f"{task_dir}/{asset_name}") # 경로 합치기 위의 경로 + 2번째 위젯의 에셋 이름
        for item in items:
            if not os.path.isdir(f"{task_dir}/{asset_name}/{item}"):
                continue
            tasks.append(item) # 
        self.ui.listWidget_tasks.clear()
        self.ui.listWidget_tasks.addItems(tasks) # 3번째 위젯에 경로를 가진 아이템 추가

    def get_scenes(self, row, col):
        project = self.ui.comboBox_project.currentText()
        asset_type = self.ui.listWidget_category.currentItem().text()
        task_type = self.ui.listWidget_tasks.currentItem().text() # 3번째 리스트 위젯의 선택된 텍스트

        indexes = self.ui.tableWidget_asset.selectedIndexes() # 2번째 위젯의 인덱스를 가져옵니다.
        for index in indexes:
            row = index.row() # 선택한 셀의 row 인덱스
            col = index.column() # 선택한 셀의 column 인덱스

            widget = self.ui.tableWidget_asset.cellWidget(row, col) # 2번째 위젯의 선택된 항목을 가져옵니다.
            childs = widget.children() # 
            for child_widget in childs: # 
                if child_widget.objectName() == "label_asset_name":
                    asset_name = child_widget.text() # 에셋 이름을 가져옵니다.
                    break

        scene_dir = f"/nas/show/{project}/assets/{asset_type}/{asset_name}/{task_type}/maya/scenes" # 씬 경로

        scene_items = os.listdir(scene_dir) # scene_items에 정의한 경로 붙이기
        scene_count = len(scene_items) # 

        self.ui.tableWidget_scenes.setRowCount(scene_count) # 4번째 위젯에 선택 항목 붙이기
        self.ui.tableWidget_scenes.setColumnCount(1)

        for row, scene_item in enumerate(scene_items):
            self.make_scene_table(scene_item, row) # 메서드에 경로를 가진 아이템을 붙인다.

    def make_scene_table(self, scene_name, row): # 경로를 가진 아이템
        # 장면을 위한 위젯 생성
        widget = QWidget()  # 위젯 생성
        hbox_layout = QHBoxLayout()  # 수평 레이아웃 생성
        image_label = QLabel()  # 이미지를 표시할 라벨 생성
        image_label.setObjectName("label_image")
        
        text_label = QLabel()  # 장면 이름을 표시할 라벨 생성
        text_label.setText(scene_name)  # 장면 이름을 텍스트로 설정
        text_label.setObjectName("label_scene_name")

        # 장면 이미지 설정
        scene_path = "/nas/rnd/pipeline/resources/logo_images/maya_logo_64px.png"
        pixmap = QPixmap(scene_path)
        scaled_pixmap = pixmap.scaled(60, 60)  # 이미지 크기 조정
        image_label.setPixmap(scaled_pixmap)  # 라벨에 이미지 설정

        # 레이아웃에 라벨 추가
        hbox_layout.addWidget(image_label)  # 이미지 라벨을 레이아웃에 추가
        hbox_layout.addWidget(text_label)  # 텍스트 라벨을 레이아웃에 추가

        # 위젯에 레이아웃 설정
        widget.setLayout(hbox_layout)
        
        # 테이블의 해당 row 위치에 위젯을 삽입
        self.ui.tableWidget_scenes.setCellWidget(row, 0, widget)

    # 메인 ui
    def load_ui(self):
        # .ui 파일 경로
        ui_file_path = "/home/rapa/My_Python/pipeline_0206/ui/loader.ui"  # .ui 파일 경로로 변경
        # .ui 파일을 QFile로 로드
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        # UI 로드
        self.ui = loader.load(ui_file)
        self.ui.show()
        # 파일을 닫음
        ui_file.close()

    # sub ui
    def sub_load_ui(self):
        ui_file_path = "/home/rapa/My_Python/pipeline_0206/ui/sub_loader.ui"
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.sub_ui = loader.load(ui_file)
        self.sub_ui.show()
        ui_file.close()   

if __name__ == "__main__":
    app = QApplication() # 하나의 스레드에서는 하나의 QApplication만 동작이 가능합니다.
    w = Loader()
    app.exec()

    