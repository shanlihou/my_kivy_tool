#coding=utf-8
import os
from kivy.resources import resource_add_path, resource_find
from kivy.core.text import LabelBase
resource_add_path(os.path.abspath('./resource'))
LabelBase.register('Roboto', 'DroidSansFallback.ttf')

from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.factory import Factory
from common import config


Builder.load_string('''
#:include kvs/DirViewWidget.kv
#:import Factory kivy.factory.Factory
<MyPopup@Popup>:
    auto_dismiss: False
    size_hint: .5, .5
    title: 'dir name'
    GridLayout:
        rows: 2
        TextInput:
            id: t_dir_name
        Button:
            text: 'Close me!'
            on_release: root.dismiss()

<MainView>:
    cols: 1
    name: 'home'
    ActionBar:
        size_hint_y: .1
        on_previous: print('prev')
        ActionView:
            use_separator: True
            ActionPrevious:
                title: 'Action Bar'
                with_previous: True
                on_press: dir_view.on_up_press()
            ActionOverflow:
            ActionGroup:
                text: '...'
                mode: 'spinner'
                ActionButton:
                    text: 'create dir'
                    on_press: root.pop_create_dir()
                ActionButton:
                    text: 'Btn6'
                ActionButton:
                    text: 'Btn7'
    DirView:
        id: dir_view
        on_path_select: root.on_path_select()
        on_all_path_deselect: root.on_all_path_deselect()
''')


class BottomBar(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = 0.1
        self.rows = 1
        self.add_button('remove', self.on_remove_press)
        self.add_button('rename', self.on_rename_press)
        self.add_button('encrypt', self.on_encrypt_press)
        self.add_button('decrypt', self.on_decrypt_press)
        self.add_button('full', self.on_full_press)

    def add_button(self, button_name, func):
        button = Factory.Button(text=button_name)
        button.bind(on_press=func)
        self.add_widget(button)

    def on_remove_press(self, *args):
        if self.parent:
            self.parent.on_remove_press()


    def on_rename_press(self, *args):
        print('rename')

    def on_encrypt_press(self, *args):
        print('encrypt')
        if self.parent:
            self.parent.on_encrypt_press()

    def on_decrypt_press(self, *args):
        print('decrypt')
        if self.parent:
            self.parent.on_decrypt_press()

    def on_full_press(self, *args):
        print('full')
        if self.parent:
            self.parent.on_full_press()


class MainView(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bottom_bar = None

    def pop_create_dir(self):
        def _func(instance):
            self.ids['dir_view'].on_create_dir(instance.ids['t_dir_name'].text)

        popup = Factory.MyPopup()
        popup.bind(on_dismiss=_func)
        popup.open()
        # print('will pop')
        # popup = Popup(title='Test popup',
        #     content=Label(text='Hello world'),
        #     size_hint=(None, None), size=(400, 400))
        # popup.open()

    def on_path_select(self):
        self.bottom_bar = BottomBar()
        self.add_widget(self.bottom_bar)

    def on_all_path_deselect(self):
        if self.bottom_bar:
            self.remove_widget(self.bottom_bar)
            self.bottom_bar = None

    def on_remove_press(self):
        self.ids['dir_view'].do_remove()

    def on_encrypt_press(self):
        self.ids['dir_view'].do_encrypt()

    def on_decrypt_press(self):
        self.ids['dir_view'].do_decrypt()

    def on_full_press(self):
        self.ids['dir_view'].do_full()


class MagToolApp(App):
    def build(self):
        return MainView()


if __name__ == '__main__':
    config.Config('EncryptTool')
    MagToolApp().run()
    # from lib import utils
    # utils.decrypt_file(r'E:\svn\Dev\xzj_win64_dev\xzj.exe')
