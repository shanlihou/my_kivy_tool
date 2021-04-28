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
import sys
sys.path.append(r'E:\shgithub\python\pythonFunc\Lib')
import bmob
import json

g_info_list = []
g_sm = None
g_rv = None

Builder.load_string('''
<AddPwdScreen>:
    rows: 2
    name: 'home'
    GridLayout:
        cols: 2
        BoxLayout:
            orientation: 'vertical'
            TextInput:
                text: 'username'
                id: t_name
            TextInput:
                text: 'password'
                id: t_pwd
            TextInput:
                text: 'desc'
                id: t_desc

        BoxLayout:
            orientation: 'vertical'
            Button:
                text: 'upload'
                on_press: root.on_upload_press()

            Button:
                text: 'clear'
                on_press: root.on_clear_press()

            Button:
                text: 'all'
                on_press: root.on_all_press()
    Label:
        text: ''
        size_hint: 0.5, 0.5

<PwdInfo>:
    cols: 3
    value: ''
    Label:
        id: t_name
    Label:
        id: t_pwd
    Label:
        id: t_desc

<RV>:
    viewclass: 'PwdInfo'
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'

<PwdListScreen>:
    rows: 2
    name: 'another'
    Button:
        text: "Go back home"
        on_release: root.manager.current = 'home'
    RV:


<ScreenManager>:
    AddPwdScreen:
    PwdListScreen:
''')

class PwdInfo(GridLayout, RecycleDataViewBehavior):
    def refresh_view_attrs(self, rv, index, data):
        super().refresh_view_attrs(rv, index, data)
        for k, v in data.items():
            self.ids[k].text = v


class AddPwdScreen(GridLayout, Screen):
    def on_clear_press(self):
        self.ids['t_name'].text = ''
        self.ids['t_pwd'].text = ''
        self.ids['t_desc'].text = ''

    def on_all_press(self):
        ret = bmob.BMOB().get('myPwd')
        ret = json.loads(ret)['results']
        global g_info_list
        g_info_list.clear()
        for pwdInfo in ret:
            host = bmob.BMOB().decrypt(pwdInfo['host'])
            name = bmob.BMOB().decrypt(pwdInfo['name'])
            pwd = bmob.BMOB().decrypt(pwdInfo['pwd'])
            g_info_list .append({'t_name': name, 't_desc': host, 't_pwd': pwd})
        print(g_info_list)
        g_sm.current = 'another'
        g_rv.data = g_info_list

    def on_upload_press(self):
        data = {'host': self.ids['t_desc'].text, 'name': self.ids['t_name'].text, 'pwd': self.ids['t_pwd'].text}
        for k, v in data.items():
            data[k] = bmob.BMOB().encrypt(v)
        data = json.dumps(data)
        bmob.BMOB().addData('myPwd', data)


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = g_info_list
        global g_rv
        g_rv = self


class PwdListScreen(GridLayout,Screen):
    pass


class MyScreenManager(ScreenManager):
    pass


class AddPwdApp(App):
    def build(self):
        global g_sm
        g_sm = MyScreenManager()
        return g_sm


if __name__ == '__main__':
    pri_name = os.path.join('secret', '.pri_191be71fff.pem')
    pub_name = os.path.join('secret', '.pub_191be71fff.pem')
    bmob.BMOB(pri_name, pub_name)
    AddPwdApp().run()
