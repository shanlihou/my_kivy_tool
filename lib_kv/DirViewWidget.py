#coding = utf-8
from kivy.uix.recycleview.views import _cached_views, _view_base_cache, _clean_cache
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.uix.spinner import Spinner
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle
import shutil
from lib import utils
from kivy.clock import Clock
from common import config
import os

class DirDropDownObj(DropDown):
    def on_select(self, *args):
        print('on select:', args)
        return False

    def on_touch_down1(self, *args):
        print('on touch down:', args)
        #super().on_touch_down(*args)
        self.dismiss()
        return True


class DirSpinner(Spinner):
    def on_text(self, *args):
        print('on text')
        return True


class DirInfoObj(RecycleDataViewBehavior, GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids['s_path_select'].bind(active=self.on_path_select_changed)

    def get_full_path(self):
        if self.parent and self.parent.parent:
            return os.path.join(self.parent.parent.cur_path, self.ids['l_path'].text)
        else:
            return self.ids['l_path'].text

    def refresh_view_attrs(self, rv, index, data):
        super().refresh_view_attrs(rv, index, data)
        old_path = self.get_full_path()
        for k, v in data.items():
            if k not in self.ids:
                continue

            self.ids[k].text = v
        print('refresh:', data)
        self.ids['s_path_select'].active = data['active']

        if data['index'] % 2:
            self.bgColor = [199 / 255, 237 / 255, 204 / 255, 205 / 255]
        else:
            self.bgColor = [220 / 255, 226 / 255, 241 / 255, 205 / 255]

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos):
            if self.parent and self.parent.parent:
                self.parent.parent.dispatch('on_dir_press', self.get_file_name())

    def get_file_name(self):
        return self.ids['l_path'].text

    @staticmethod
    def on_path_select_changed(instance, value):
        dir_info_obj = instance.parent
        print('on changed:', dir_info_obj.ids['l_path'].text, instance, value, dir_info_obj.parent)
        if dir_info_obj.parent and dir_info_obj.parent.parent:
            dir_info_obj.parent.parent.dispatch('on_dir_select_changed', dir_info_obj.get_file_name(), value)

    def set_is_active(self, is_active):
        self.ids['s_path_select'].active = is_active


class DirPathData(object):
    def __init__(self, filename, index):
        self.filename = filename
        self.index = index
        self.active = False

    def to_dict(self):
        return {
            'l_path': self.filename,
            'index': self.index,
            'active': self.active,
        }


class DirPathRecycleObj(RecycleView):
    cur_dir = StringProperty('')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cur_dir = os.path.abspath(os.getcwd())
        self.cur_dir = config.Config().get('cur_dir', self.cur_dir)
        self.register_event_type('on_dir_press')
        self.register_event_type('on_dir_select_changed')
        self.change_dir(self.cur_dir)
        self.select_set = set()

    def on_dir_press(self, obj_name):
        new_path = os.path.join(self.cur_dir, obj_name)
        if os.path.isdir(new_path):
            self.change_dir(new_path)
        return True

    def clear_cache(self, *args):
        _clean_cache()

    def change_dir(self, new_dir):
        try:
            self.file_data_dict = {}
            for index, i in enumerate(os.listdir(new_dir)):
                self.file_data_dict[i] = DirPathData(i, index)

            print(self.file_data_dict)

            _data = [None] * len(self.file_data_dict)
            for v in self.file_data_dict.values():
                _data[v.index] = v.to_dict()

            self.data = _data
            self.cur_dir = new_dir
            self.select_set = set()
            if self.parent:
                self.parent.dispatch('on_all_path_deselect')
            config.Config().set_val('cur_dir', self.cur_dir)
        except Exception as e:
            print(e)

    def on_up_press(self, *args):
        newdir = os.path.dirname(self.cur_dir)
        self.change_dir(newdir)

    def on_pop_press(self, *args):
        print('on pop')

    def on_create_dir(self, dir_name):
        path = os.path.join(self.cur_dir, dir_name)
        try:
            os.mkdir(path)
            self.change_dir(self.cur_dir)
        except:
            pass

    def on_dir_select_changed(self, filename, value):
        data_val = self.file_data_dict[filename]
        data_val.active = value
        print('on_dir_select_changed', data_val.to_dict(), self.data[data_val.index])
        self.data[data_val.index]['active'] = data_val.active

        if value:
            self.select_set.add(filename)
            if len(self.select_set) == 1 and self.parent:
                self.parent.dispatch('on_path_select')
        else:
            self.select_set.discard(filename)
            if len(self.select_set) == 0:
                self.parent.dispatch('on_all_path_deselect')

    def do_remove(self):
        is_change = False
        for path in self.select_set:
            full = os.path.join(self.cur_dir, path)
            try:
                shutil.rmtree(full)
                is_change = True
            except:
                print('rm failed:', path)

        if is_change:
            self.change_dir(self.cur_dir)

    def do_encrypt(self):
        is_change = False
        for path in self.select_set:
            full = os.path.join(self.cur_dir, path)
            try:
                utils.encrypt_file(full)
                is_change = True
            except Exception as e:
                print('enc except:', e)

        if is_change:
            self.change_dir(self.cur_dir)

    def do_decrypt(self):
        is_change = False
        for path in self.select_set:
            full = os.path.join(self.cur_dir, path)
            try:
                utils.decrypt_file(full)
                is_change = True
            except Exception as e:
                print('dec except:', e)

        if is_change:
            self.change_dir(self.cur_dir)

    def do_full(self):
        is_set_true = len(self.data) != len(self.select_set)
        for child in self.children:
            for _child in child.children:
                if hasattr(_child, 'set_is_active'):
                    getattr(_child, 'set_is_active')(is_set_true)

        for v in self.file_data_dict.values():
            v.active = is_set_true
            if is_set_true:
                self.select_set.add(v.filename)
            else:
                self.select_set.discard(v.filename)

        for _data in self.data:
            _data['active'] = is_set_true

        self.refresh_from_data()

        if not is_set_true:
            self.parent.dispatch('on_all_path_deselect')


class DirObj(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_path_select')
        self.register_event_type('on_all_path_deselect')
        # Clock.schedule_once(self.change_dir, 5)

    def on_up_press(self):
        self.ids['r_dir_view'].on_up_press()

    def on_create_dir(self, dir_name):
        self.ids['r_dir_view'].on_create_dir(dir_name)

    def on_path_select(self, *args):
        pass

    def on_all_path_deselect(self, *args):
        pass

    def get_selected_path(self):
        return list(self.ids['r_dir_view'].select_set)

    def do_remove(self):
        self.ids['r_dir_view'].do_remove()

    def do_encrypt(self):
        self.ids['r_dir_view'].do_encrypt()

    def do_decrypt(self):
        self.ids['r_dir_view'].do_decrypt()

    def do_full(self):
        self.ids['r_dir_view'].do_full()

