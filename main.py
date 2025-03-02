from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

if platform == "android":
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    WebChromeClient = autoclass('android.webkit.WebChromeClient')
    LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
    View = autoclass('android.view.View')

# KV string dengan transisi slide
KV = '''
ScreenManager:
    id: screen_manager
    transition: SlideTransition()
'''

class WebViewTab(Screen):
    """Kelas untuk mengelola tab WebView individual."""
    url = StringProperty("")
    webview = ObjectProperty(None)

    def on_enter(self):
        """Dipanggil saat screen menjadi aktif."""
        if platform == "android":
            self.create_webview()

    def create_webview(self):
        """Membuat dan menginisialisasi WebView."""
        try:
            if not self.webview:
                activity = PythonActivity.mActivity
                self.webview = WebView(activity)
                
                # Setup WebView
                self.webview.getSettings().setJavaScriptEnabled(True)
                self.webview.setWebViewClient(WebViewClient())
                self.webview.setWebChromeClient(WebChromeClient())
                
                # Load URL
                if not self.url.startswith(('http://', 'https://')):
                    self.url = 'https://' + self.url
                self.webview.loadUrl(self.url)
                
                # Tambahkan WebView ke layout
                params = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
                activity.addContentView(self.webview, params)
            else:
                self.webview.setVisibility(View.VISIBLE)
        except Exception as e:
            print(f"Error creating WebView: {str(e)}")

    def hide_webview(self):
        """Menyembunyikan WebView saat tab tidak aktif."""
        if self.webview:
            self.webview.setVisibility(View.GONE)

    def execute_find_in_page(self, text):
        """Mencari teks dalam halaman."""
        if self.webview and text:
            self.webview.findAllAsync(text)
    
    def find_next(self, forward=True):
        """Mencari hasil berikutnya/sebelumnya."""
        if self.webview:
            self.webview.findNext(forward)

    def remove_webview(self):
        """Membersihkan WebView saat tab ditutup."""
        if self.webview:
            parent = self.webview.getParent()
            if parent:
                parent.removeView(self.webview)
            self.webview = None

    def can_go_back(self):
        """Mengecek apakah bisa kembali ke halaman sebelumnya."""
        return self.webview and self.webview.canGoBack()

    def go_back(self):
        """Kembali ke halaman sebelumnya."""
        if self.can_go_back():
            self.webview.goBack()

class MainApp(MDApp):
    """Aplikasi utama untuk multi-tab web wrapper."""
    dialog = None
    find_overlay = None
    touch_start_x = 0.0

    def build(self):
        """Membangun UI aplikasi."""
        self.title = "Multi-Tab Web Wrapper"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        self.screen_manager = Builder.load_string(KV)
        self.add_new_tab("https://www.example.com")
        
        # Setup touch events untuk gesture swipe
        Window.bind(on_touch_down=self.on_touch_down)
        Window.bind(on_touch_up=self.on_touch_up)
        
        # Floating buttons
        self.tab_button = MDFloatingActionButton(
            icon="tab",
            pos_hint={"x": 0.05, "y": 0.05},
            on_release=self.open_tab_dialog
        )
        self.find_button = MDFloatingActionButton(
            icon="magnify",
            pos_hint={"x": 0.85, "y": 0.05},
            on_release=self.show_find_overlay
        )
        
        root = FloatLayout()
        root.add_widget(self.screen_manager)
        root.add_widget(self.tab_button)
        root.add_widget(self.find_button)
        return root

    def on_touch_down(self, instance, touch):
        """Menangkap posisi awal gesture swipe."""
        self.touch_start_x = touch.x
        return False

    def on_touch_up(self, instance, touch):
        """Menangani gesture swipe untuk navigasi tab."""
        delta_x = touch.x - self.touch_start_x
        if abs(delta_x) > 100:  # threshold 100 pixel
            current_index = self.screen_manager.screens.index(self.screen_manager.current_screen)
            
            if delta_x > 0 and current_index > 0:  # Swipe kanan
                self.screen_manager.transition.direction = 'right'
                self.screen_manager.current = self.screen_manager.screens[current_index - 1].name
            elif delta_x < 0 and current_index < len(self.screen_manager.screens) - 1:  # Swipe kiri
                self.screen_manager.transition.direction = 'left'
                self.screen_manager.current = self.screen_manager.screens[current_index + 1].name
        return False

    def add_new_tab(self, url):
        """Menambah tab baru."""
        current_screen = self.screen_manager.current_screen
        if current_screen and isinstance(current_screen, WebViewTab):
            current_screen.hide_webview()
        
        tab_name = f"tab_{len(self.screen_manager.screens)+1}"
        new_tab = WebViewTab(name=tab_name, url=url)
        self.screen_manager.add_widget(new_tab)
        self.screen_manager.current = tab_name
        Clock.schedule_once(lambda dt: new_tab.on_enter(), 0.5)

    def open_tab_dialog(self, instance):
        """Membuka dialog manajemen tab."""
        content = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        for screen in self.screen_manager.screens:
            if isinstance(screen, WebViewTab):
                btn = MDFlatButton(
                    text=screen.url,
                    on_release=lambda x, scr=screen: self.switch_to_tab(scr)
                )
                content.add_widget(btn)
        
        add_btn = MDFlatButton(text="Tambah Tab Baru", on_release=self.prompt_new_tab)
        content.add_widget(add_btn)
        
        self.dialog = MDDialog(
            title="Manajemen Tab",
            type="custom",
            content_cls=content,
            size_hint=(0.8, 0.5)
        )
        self.dialog.open()

    def switch_to_tab(self, screen):
        """Beralih ke tab yang dipilih."""
        if self.screen_manager.current_screen and isinstance(self.screen_manager.current_screen, WebViewTab):
            self.screen_manager.current_screen.hide_webview()
        self.screen_manager.current = screen.name
        screen.webview.setVisibility(View.VISIBLE)
        self.dialog.dismiss()

    def prompt_new_tab(self, instance):
        """Meminta URL untuk tab baru."""
        self.dialog.dismiss()
        self.new_tab_dialog = MDDialog(
            title="Masukkan URL",
            type="custom",
            content_cls=MDTextField(hint_text="https://www.example.com", text="https://"),
            buttons=[
                MDFlatButton(text="BATAL", on_release=lambda x: self.new_tab_dialog.dismiss()),
                MDFlatButton(text="BUAT", on_release=self.create_tab_from_dialog)
            ]
        )
        self.new_tab_dialog.open()

    def create_tab_from_dialog(self, instance):
        """Membuat tab baru dari dialog input."""
        url_field = self.new_tab_dialog.content_cls
        url = url_field.text
        self.new_tab_dialog.dismiss()
        self.add_new_tab(url)

    def show_find_overlay(self, instance):
        """Menampilkan overlay pencarian dalam halaman."""
        content = MDBoxLayout(orientation="horizontal", spacing="10dp")
        self.search_field = MDTextField(hint_text="Cari di halaman", size_hint_x=0.7)
        btn_prev = MDFlatButton(text="Prev", on_release=lambda x: self.find_prev())
        btn_next = MDFlatButton(text="Next", on_release=lambda x: self.find_next())
        btn_close = MDFlatButton(text="Tutup", on_release=lambda x: self.close_find_overlay())
        
        content.add_widget(self.search_field)
        content.add_widget(btn_prev)
        content.add_widget(btn_next)
        content.add_widget(btn_close)
        
        self.find_overlay = MDDialog(
            title="Find in Page",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None)
        )
        self.find_overlay.open()
        self.search_field.bind(text=self.on_search_text)

    def on_search_text(self, instance, value):
        """Handler untuk perubahan teks pencarian."""
        current_tab = self.screen_manager.current_screen
        if isinstance(current_tab, WebViewTab):
            current_tab.execute_find_in_page(value)

    def find_next(self):
        """Mencari hasil berikutnya."""
        current_tab = self.screen_manager.current_screen
        if isinstance(current_tab, WebViewTab):
            current_tab.find_next(True)

    def find_prev(self):
        """Mencari hasil sebelumnya."""
        current_tab = self.screen_manager.current_screen
        if isinstance(current_tab, WebViewTab):
            current_tab.find_next(False)

    def close_find_overlay(self):
        """Menutup overlay pencarian."""
        if self.find_overlay:
            self.find_overlay.dismiss()
            self.find_overlay = None

    def on_stop(self):
        """Membersihkan resources saat aplikasi ditutup."""
        for screen in self.screen_manager.screens:
            if isinstance(screen, WebViewTab):
                screen.remove_webview()

if __name__ == '__main__':
    MainApp().run()
