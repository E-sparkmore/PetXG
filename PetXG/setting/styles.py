from . import config

audio_ui_light_style = '''
    QListWidget {
        font-weight: bold;
        background-color: "white";
        outline: none;
    }
    QListWidget::Item {
        padding: 6px;
        color: black;
        border-bottom: 2px solid #AAA;
    }
    QListWidget::Item::hover {
        color: black;
        background-color: #EEE;
    }
    QListWidget::Item::selected {
        color: black;
        background-color: #EEE;
    }
    QSlider {
        width: 25px;
    }
    AudioWidget {
        background-color: aliceblue;
    }
    QLabel {
        color: black;
    }
'''

audio_ui_dark_style = '''
    QListWidget {
        font-weight: bold;
        background-color: #2B2B2B;
        outline: none;
    }
    QListWidget::Item {
        padding: 6px;
        color: white;
        border-bottom: 2px solid #444;
    }
    QListWidget::Item::hover {
        color: white;
        background-color: #444;
    }
    QListWidget::Item::selected {
        color: white;
        background-color: #444;
    }
    QSlider {
        width: 25px;
    }
    AudioWidget {
        background-color: #231F1A;
    }
    QLabel {
        color: white;
    }
'''

pet_label_style = '''
    QMenu#DIY_menu {
        background-color:transparent;
        border-radius: 20px;
        padding-top:20px;
        padding-left:15px;
        padding-right:10px;
        padding-bottom:40px;
        height: 200px;
        background-image: url("''' + config.datafile + '''menu_skin.png");
        background-repeat: no-repeat;
    }
    QMenu#DIY_menu::item {
        font-weight: 600;
        font-size:12px;
        padding:2px;
        margin: 2px;
        margin-right:60px;
        padding-left:20px;
        padding-right: 0px;
        color: black;
    }
    QMenu#DIY_menu::item:selected{
        background-color: rgba(20,20,20,0.1);
    }
    QMenu#DIY_menu::item::QToolButton {
        padding-left:6px;
    }
    QMenu#DIY_menu::item:!enabled {
        color: gray;
    }
'''