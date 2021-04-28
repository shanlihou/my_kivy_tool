#coding=utf-8
import os
from kivy.resources import resource_add_path, resource_find
from kivy.core.text import LabelBase
resource_add_path(os.path.abspath('./resource'))
LabelBase.register('Roboto', 'DroidSansFallback.ttf')

from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.core.clipboard import Clipboard
from lib import magnet
from common import config

g_mag_listview = None

Builder.load_string('''
<MainView>:
    rows: 3
    name: 'home'
    SearchView:
    Label:
        size_hint_y: 0.1
        id: l_state
    MagListView:

<SearchView>:
    cols: 2
    size_hint_y: 0.1
    TextInput:
        id: t_searchContent
    Button:
        text: 'search'
        on_press: root.on_search()
        size_hint_x: 0.1

<MagInfo>:
    cols: 2
    Label:
        id: l_name
    Label:
        id: l_size
        size_hint_x: 0.1

<MagListView>:
    viewclass: 'MagInfo'
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'

''')

class SearchView(GridLayout):
    def on_search(self):
        code = self.ids['t_searchContent'].text
        self.parent.ids['l_state'].text = 'start searching'
        ret = magnet.get_all_magnet(code)
        datas = []
        for i in ret:
            datas.append({
                'l_name': i[1],
                'l_size': i[2],
                'mag': i[0],
            })

        g_mag_listview.data = datas

        self.parent.ids['l_state'].text = 'finish search:{}'.format(len(datas))

class MagInfo(GridLayout, RecycleDataViewBehavior):
    def refresh_view_attrs(self, rv, index, data):
        super().refresh_view_attrs(rv, index, data)
        for k, v in data.items():
            if k not in self.ids:
                continue

            self.ids[k].text = v

        self.mag = data['mag']

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos):
            print('on touch down:', self.mag)
            Clipboard.copy(self.mag)


class MagListView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        global g_mag_listview
        g_mag_listview = self


class MainView(GridLayout):
    pass


class MagToolApp(App):
    def build(self):
        return MainView()


if __name__ == '__main__':
    config.Config('MagToolConfig')
    MagToolApp().run()
    # magnet.main()
    # magnet.get_cur_uri(True)