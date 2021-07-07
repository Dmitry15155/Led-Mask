from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.colorpicker import ColorPicker
from kivy.core.window import Window
from kivy.storage.jsonstore import JsonStore
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.togglebutton import ToggleButton
import bluetooth
class MainApp(App):

    def on_start(self):
        self.store = JsonStore('image.json')


    def build(self):
        self.flag = True
        Window.bind(mouse_pos=self.on_mouse_move)
        self.color = [.14, .89, .98, 1]
        # Первая страница
        self.main_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.b = []
        # Поле рисования
        for i in range(8):
            h_layout = BoxLayout(spacing=10)
            for j in range(16):
                button = Button(text="", background_normal="", background_color=[.16, .17, .17, 1])
                self.b.append(button)
                button.bind(on_press=self.on_button_touch_up)
                h_layout.add_widget(button)

            self.main_layout.add_widget(h_layout)
        # конец поля рисования

        # Кнопки
        buttons = ["bluetooth", "Save", "Clear", "Open", "Palette"]
        h_layout = BoxLayout(spacing=10)
        for i in buttons:
            button = Button(text=i, pos_hint={"center_x": 0.5, "center_y": 0.5})
            button.bind(on_press=self.f_button)
            h_layout.add_widget(button)
        self.main_layout.add_widget(h_layout)
        # конец кнопок
        # Конец первой страницы

        return self.main_layout

    def on_button_touch_up(self, instance):

        if instance.background_color == [.16, .17, .17, 1]:
            instance.background_normal = ""
            instance.background_color = self.color
        else:
            instance.background_color = [.16, .17, .17, 1]
        self.send_data()

    def f_button(self, instance):
        if instance.text == "Clear":
            for i in self.b:
                i.background_color = [.16, .17, .17, 1]
            try:
                self.soket.send('0')
            except:
                pass
        if instance.text == "Palette":
            layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
            self.palette = ColorPicker()
            button = Button(text="Close", size_hint=(.1, .1))
            layout.add_widget(self.palette)
            layout.add_widget(button)
            self.popup = Popup(title="Palette", content=layout)
            self.popup.open()
            self.flag = False
            button.bind(on_press=self.exit_palette)
        if instance.text == "Save":
            layout = AnchorLayout(anchor_x='center', anchor_y='center')
            self.save = Popup(title="Save", content=layout)
            self.text_save = TextInput(multiline=False, size_hint=(.5, .1))
            layout.add_widget(self.text_save)
            h_layout = BoxLayout(padding=20)
            buttons = ["Close", "Save"]
            for i in buttons:
                button = Button(text=i, size_hint=(.1, .1))
                h_layout.add_widget(button)
                button.bind(on_press=self.layout_save)
            layout.add_widget(h_layout)
            self.save.open()
            self.flag = False

        if instance.text == "Open":
            layout = BoxLayout(orientation="vertical", padding=20)
            self.load = Popup(title="Load", content=layout)
            self.del_h_layout = BoxLayout(padding=20)
            for i in self.store.keys():
                button = Button(text=i, size_hint=(.5, .5))
                button.bind(on_press=self.load_button)
                self.del_h_layout.add_widget(button)
            layout.add_widget(self.del_h_layout)

            h_layout = BoxLayout(padding=20)
            button = Button(text="Close", size_hint=(.5, .5))
            button.bind(on_press=self.ex_load)
            h_layout.add_widget(button)
            self.del_button = ToggleButton(text="Delete", group="delete", size_hint=(.5, .5))
            h_layout.add_widget(self.del_button)
            layout.add_widget(h_layout)
            self.load.open()
            self.flag = False

        if instance.text == "bluetooth":
            layout = BoxLayout(orientation="vertical")
            self.blue_popup = Popup(title="bluetooth", content=layout)
            self.find = bluetooth.discover_devices(lookup_names=True)
            self.devices = {}
            for i in self.find:
                name = i[1]
                self.devices[name] = i[0]
                butt = Button(text=name)
                butt.bind(on_press=self.connect_devices)
                layout.add_widget(butt)
            close = Button(text="Close")
            close.bind(on_press=self.close_bluetooth)
            layout.add_widget(close)
            self.blue_popup.open()
            self.flag = False




    def exit_palette(self, instance):
        self.color = self.palette.color
        self.popup.dismiss()
        self.flag = True

    def on_mouse_move(self, window, pos):
        for i in self.b:
            x, y = pos
            x = int(x)
            y = int(y)
            a = int(i.center_x)
            b = int(i.center_y)
            w = int(i.width // 2)
            h = int(i.height // 2)
            if a - w < x < a + w and b - h < y < b + h and self.flag:
                if i.background_color == [.16, .17, .17, 1]:
                    i.background_normal = ""
                    i.background_color = self.color
        self.send_data()

    def layout_save(self, instance):
        if instance.text == "Save":
            colors = []
            for i in self.b:
                colors.append(i.background_color)
            self.save.dismiss()
            self.flag = True
            self.store.put(self.text_save.text, colors=colors)

        if instance.text == "Close":
            self.save.dismiss()
            self.flag = True

    def load_button(self, instance):
        if self.del_button.state != "down":
            colors = self.store.get(instance.text)["colors"]
            for i in range(len(self.b)):
                self.b[i].background_color = colors[i]
            self.load.dismiss()
            self.flag = True
        else:
            self.store.delete(instance.text)
            self.del_h_layout.remove_widget(instance)

    def ex_load(self, instance):
        self.load.dismiss()
        self.flag = True


    def connect_devices(self, instance):
        name = instance.text
        adress = self.devices.get(name)
        self.soket = bluetooth.BluetoothSocket()
        try:
            self.soket.connect((adress, 1))
            self.blue_popup.dismiss()
            self.flag = True
        except:
            pass



    def send_data(self):
        try:
            flag = True
            for i in self.b:
                if i.background_color != [.16, .17, .17, 1]:
                    flag = False
                    break
            if flag:
                self.soket.send('0')
            else:
                self.soket.send('1')
        except:
            pass

    def close_bluetooth(self, instance):
        self.blue_popup.dismiss()
        self.flag = True


MainApp().run()
