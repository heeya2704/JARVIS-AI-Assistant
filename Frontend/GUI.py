from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, 
                             QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFrame, QLabel, QSizePolicy)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from dotenv import load_dotenv
import sys
import os

# Load environment variables
load_dotenv()
Assistantname = os.getenv("Assistantname", "Assistant")
old_chat_message = ""

# Get the actual script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script running from: {script_dir}")

# Build paths relative to script location
TempDirPath = os.path.join(script_dir, "Files")
GraphicsDirPath = os.path.join(script_dir, "Graphics")

# Create directories if they don't exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

print(f"Looking for graphics in: {GraphicsDirPath}")
print(f"Looking for temp files in: {TempDirPath}")


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whom', 
                     'can you', "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '.'
        else:
            new_query += '.'

    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    filepath = TempDirectoryPath('Mic.data')
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(Command)


def GetMicrophoneStatus():
    filepath = TempDirectoryPath('Mic.data')
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            Status = file.read().strip()
        return Status
    except FileNotFoundError:
        return "False"


def SetAssistantStatus(Status):
    filepath = os.path.join(TempDirPath, 'Status.data')
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(Status)


def GetAssistantStatus():
    filepath = os.path.join(TempDirPath, 'Status.data')
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            Status = file.read()
        return Status
    except FileNotFoundError:
        return ""


def MicButtonInitiated():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def GraphicsDirectoryPath(Filename):
    path = os.path.join(GraphicsDirPath, Filename)
    return path


def TempDirectoryPath(Filename):
    path = os.path.join(TempDirPath, Filename)
    return path


def ShowTextToScreen(Text):
    filepath = os.path.join(TempDirPath, 'Responses.data')
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(Text)


class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        gif_path = os.path.join(GraphicsDirPath, "Jarvis.gif")
        
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            max_gif_size_W = 480
            max_gif_size_H = 270
            movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            print(f"Warning: GIF not found at {gif_path}")
            
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }

        """)

    def loadMessages(self):
        global old_chat_message
        try:
            filepath = os.path.join(TempDirPath, 'Responses.data')
            with open(filepath, 'r', encoding='utf-8') as file:
                messages = file.read()
            if messages and messages != old_chat_message:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            filepath = os.path.join(TempDirPath, 'Status.data')
            with open(filepath, 'r', encoding='utf-8') as file:
                messages = file.read()
            self.label.setText(messages)
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        
        if message.startswith('<') and message.endswith('>'):
            cursor.insertHtml(message + "<br>")
        else:
            cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        gif_path = os.path.join(GraphicsDirPath, 'Jarvis.gif')
        
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            gif_label.setMovie(movie)
            max_gif_size_H = int(screen_width / 16 * 9)
            movie.setScaledSize(QSize(screen_width, max_gif_size_H))
            gif_label.setAlignment(Qt.AlignCenter)
            movie.start()
        else:
            print(f"Warning: GIF not found at {gif_path}")

        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.icon_label = QLabel()
        self.toggled = True
        self.load_icon(os.path.join(GraphicsDirPath, 'Mic_on.png'), 60, 60)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom: 0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)

        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        try:
            filepath = os.path.join(TempDirPath, 'Status.data')
            with open(filepath, 'r', encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except FileNotFoundError:
            pass

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                new_pixmap = pixmap.scaled(width, height)
                self.icon_label.setPixmap(new_pixmap)
            else:
                print(f"Warning: Failed to load image at {path}")
        else:
            print(f"Warning: Image file not found at {path}")

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(os.path.join(GraphicsDirPath, 'Mic_on.png'), 60, 60)
            MicButtonInitiated()
        else:
            self.load_icon(os.path.join(GraphicsDirPath, 'Mic_off.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.current_screen = None
        self.draggable = True
        self.offset = None
        self.initUI()

    def showMessageScreen(self):
        self.stacked_widget.setCurrentIndex(1)

    def showInitialScreen(self):
        self.stacked_widget.setCurrentIndex(0)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        # Home button
        home_button = QPushButton()
        home_icon_path = os.path.join(GraphicsDirPath, 'Home.png')
        if os.path.exists(home_icon_path):
            home_icon = QIcon(home_icon_path)
            home_button.setIcon(home_icon)
        home_button.setText("   Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")
        home_button.clicked.connect(self.showInitialScreen)

        # Message button
        message_button = QPushButton()
        message_icon_path = os.path.join(GraphicsDirPath, 'Message.png')
        if os.path.exists(message_icon_path):
            message_icon = QIcon(message_icon_path)
            message_button.setIcon(message_icon)
        message_button.setText("   Message")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")
        message_button.clicked.connect(self.showMessageScreen)

        # Minimize button
        minimize_button = QPushButton()
        minimize_icon_path = os.path.join(GraphicsDirPath, 'Minimize.png')
        if os.path.exists(minimize_icon_path):
            minimize_icon = QIcon(minimize_icon_path)
            minimize_button.setIcon(minimize_icon)
        minimize_button.setFlat(True)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        # Maximize button
        self.maximize_button = QPushButton()
        maximize_icon_path = os.path.join(GraphicsDirPath, 'Maximize.png')
        restore_icon_path = os.path.join(GraphicsDirPath, 'Restore.png')
        
        self.maximize_icon = QIcon()
        self.restore_icon = QIcon()
        
        if os.path.exists(maximize_icon_path):
            self.maximize_icon = QIcon(maximize_icon_path)
            
        if os.path.exists(restore_icon_path):
            self.restore_icon = QIcon(restore_icon_path)
        
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        # Close button
        close_button = QPushButton()
        close_icon_path = os.path.join(GraphicsDirPath, 'Close.png')
        if os.path.exists(close_icon_path):
            close_icon = QIcon(close_icon_path)
            close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
    

