import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.graphics import Color, Ellipse
from kivy.core.image import Image as CoreImage
from kivy.properties import BooleanProperty, NumericProperty, ListProperty

import cv2
import numpy as np
import os
import json

# Definición de las clases (etiquetas) disponibles
CLASSES = [
    {"name": "Verde", "rgb": (0, 255, 0)},
    {"name": "Rojo", "rgb": (255, 0, 0)},
    {"name": "Azul", "rgb": (0, 0, 255)}
]

class ImageScatter(Scatter):
    """
    Widget que contiene la imagen y permite agregar marcadores (círculos) en modo edición.
    Se usa para habilitar zoom y traslación.
    """
    edit_mode = BooleanProperty(False)
    edit_radius = NumericProperty(20)
    current_class_index = NumericProperty(0)
    current_color = ListProperty([0, 1, 0])  # Color normalizado (para Verde)

    def __init__(self, **kwargs):
        super(ImageScatter, self).__init__(**kwargs)
        self.do_rotation = False  # Rotación deshabilitada
        self.markers = []  # Cada marcador es un dict con 'pos', 'class' y 'color'
        self.marker_callback = None  # Callback para actualizar resultados al agregar marcador
        self.image_widget = Image(allow_stretch=True)
        self.add_widget(self.image_widget)
        self.bind(transform=self.redraw_markers)

    def load_texture(self, texture, image_size):
        """
        Carga la textura y ajusta el tamaño del widget.
        """
        self.image_widget.texture = texture
        self.image_widget.size = image_size
        self.size = image_size
        self.markers = []  # Reinicia marcadores al cargar nueva imagen
        self.redraw_markers()

    def redraw_markers(self, *args):
        """
        Redibuja todos los marcadores sobre la imagen.
        """
        self.canvas.after.clear()
        for marker in self.markers:
            # Convertir color de 0-255 a escala [0,1]
            r, g, b = [c / 255.0 for c in marker['color']]
            with self.canvas.after:
                Color(r, g, b, 1)
                Ellipse(pos=(marker['pos'][0] - self.edit_radius, marker['pos'][1] - self.edit_radius),
                        size=(self.edit_radius * 2, self.edit_radius * 2))

    def on_touch_down(self, touch):
        """
        En modo edición, al tocar se agrega un marcador en la posición correspondiente.
        """
        if self.edit_mode and self.image_widget.collide_point(*self.to_widget(*touch.pos)):
            local = self.to_local(*touch.pos)
            self.markers.append({
                "pos": local,
                "class": self.current_class_index,
                "color": CLASSES[self.current_class_index]["rgb"]
            })
            self.redraw_markers()
            if self.marker_callback:
                self.marker_callback()
            return True
        return super(ImageScatter, self).on_touch_down(touch)

class VisualTaggerApp(App):
    """
    Aplicación principal que integra la interfaz y la lógica de edición.
    """
    def build(self):
        self.title = "Visual Tagger (Kivy)"
        self.original_image = None  # Imagen original cargada con OpenCV
        self.image_path = None

        root = BoxLayout(orientation='vertical')
        
        # Barra superior con controles
        top_bar = BoxLayout(size_hint_y=0.1)
        self.load_button = Button(text="Seleccionar desde Galería")
        self.load_button.bind(on_release=self.open_file_chooser)
        self.edit_toggle = Button(text="Modo edición OFF")
        self.edit_toggle.bind(on_release=self.toggle_edit_mode)
        self.save_button = Button(text="Guardar edición")
        self.save_button.bind(on_release=self.save_edit)
        self.save_button.disabled = True
        self.title_input = TextInput(hint_text="Título (opcional)", size_hint_x=0.4)
        self.class_spinner = Spinner(text=CLASSES[0]["name"],
                                     values=[cls["name"] for cls in CLASSES],
                                     size_hint_x=0.3)
        self.class_spinner.bind(text=self.on_class_change)
        
        top_bar.add_widget(self.load_button)
        top_bar.add_widget(self.edit_toggle)
        top_bar.add_widget(self.save_button)
        top_bar.add_widget(self.title_input)
        top_bar.add_widget(self.class_spinner)
        root.add_widget(top_bar)

        # Área central: widget scatter con la imagen
        self.scatter = ImageScatter()
        self.scatter.do_scale = True
        self.scatter.do_translation = True
        # Asignar callback para actualizar resultados al agregar marcador
        self.scatter.marker_callback = self.update_results
        root.add_widget(self.scatter)

        # Sección de resultados en acordeón (desplegable)
        self.accordion = Accordion(size_hint_y=0.2)
        self.results_item = AccordionItem(title="Resultados (desplegar)")
        self.results_label = Label(text="Resultados:\n0 marcadores", halign="left")
        self.results_item.add_widget(self.results_label)
        self.accordion.add_widget(self.results_item)
        root.add_widget(self.accordion)

        return root

    def on_class_change(self, spinner, text):
        """
        Actualiza la clase actual según la selección del usuario.
        """
        for index, cls in enumerate(CLASSES):
            if cls["name"] == text:
                self.scatter.current_class_index = index
                # Actualiza también el color normalizado
                r, g, b = [c / 255.0 for c in cls["rgb"]]
                self.scatter.current_color = [r, g, b]
                break

    def open_file_chooser(self, instance):
        """
        Abre la galería nativa para seleccionar una imagen.
        """
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.handle_selection)
        except Exception as e:
            self.show_info("Error", "El selector de archivos no está disponible.")

    def handle_selection(self, selection):
        """
        Callback para manejar la selección de imagen desde la galería.
        """
        if selection:
            self.image_path = selection[0]
            self.load_image(self.image_path)

    def load_image(self, path):
        """
        Carga la imagen con OpenCV, la convierte a textura y la muestra.
        """
        self.original_image = cv2.imread(path)
        if self.original_image is None:
            self.show_info("Error", "No se pudo cargar la imagen.")
            return
        rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        texture = self.cv2_to_texture(rgb, (w, h))
        self.scatter.load_texture(texture, (w, h))
        self.save_button.disabled = False
        self.edit_toggle.text = "Modo edición OFF"
        self.scatter.edit_mode = False
        self.results_label.text = "Resultados:\n0 marcadores"

    def cv2_to_texture(self, cv2_img, size):
        """
        Convierte una imagen OpenCV (numpy array) a textura de Kivy.
        """
        buf = cv2_img.tobytes()
        from kivy.core.image import Texture
        tex = Texture.create(size=size, colorfmt='rgb')
        tex.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        tex.flip_vertical()
        return tex

    def toggle_edit_mode(self, instance):
        """
        Alterna el modo edición y actualiza la interfaz.
        """
        self.scatter.edit_mode = not self.scatter.edit_mode
        if self.scatter.edit_mode:
            self.edit_toggle.text = "Modo edición ON"
        else:
            self.edit_toggle.text = "Modo edición OFF"
        self.update_results()

    def update_results(self):
        """
        Calcula y muestra el conteo de marcadores por clase.
        """
        counts = {cls["name"]: 0 for cls in CLASSES}
        for marker in self.scatter.markers:
            class_index = marker["class"]
            counts[CLASSES[class_index]["name"]] += 1
        total = sum(counts.values())
        results_text = "Resultados:\n"
        for cls_name, count in counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            results_text += f"{cls_name}: {count} ({percentage:.2f}%)\n"
        results_text += f"Total: {total}"
        self.results_label.text = results_text

    def save_edit(self, instance):
        """
        Al presionar guardar, se abre un popup de exportación para elegir la acción:
         - Guardar imagen y resultados  
         - Guardar imagen únicamente  
         - Guardar resultados únicamente  
         - Enviar por WhatsApp
        """
        self.open_export_popup()

    def open_export_popup(self):
        """
        Crea y muestra el popup con las opciones de exportación.
        """
        content = BoxLayout(orientation='vertical')
        label = Label(text="Selecciona la acción de exportación:")
        content.add_widget(label)
        btn_layout = BoxLayout(orientation='vertical', size_hint_y=0.8)
        btn_both = Button(text="Guardar imagen y resultados")
        btn_image = Button(text="Guardar imagen únicamente")
        btn_results = Button(text="Guardar resultados únicamente")
        btn_whatsapp = Button(text="Enviar por WhatsApp")
        btn_layout.add_widget(btn_both)
        btn_layout.add_widget(btn_image)
        btn_layout.add_widget(btn_results)
        btn_layout.add_widget(btn_whatsapp)
        content.add_widget(btn_layout)
        popup = Popup(title="Exportar", content=content, size_hint=(0.8, 0.8))
        btn_both.bind(on_release=lambda x: self.perform_export("both", popup))
        btn_image.bind(on_release=lambda x: self.perform_export("image", popup))
        btn_results.bind(on_release=lambda x: self.perform_export("results", popup))
        btn_whatsapp.bind(on_release=lambda x: self.perform_export("whatsapp", popup))
        popup.open()

    def perform_export(self, option, popup):
        """
        Realiza la exportación según la opción elegida.
        """
        popup.dismiss()
        # Dibuja los marcadores sobre la imagen original
        final_img = self.original_image.copy()
        for marker in self.scatter.markers:
            pos = marker["pos"]
            x, y = int(pos[0]), int(pos[1])
            radius = int(self.scatter.edit_radius)
            color = marker["color"]
            bgr = (color[2], color[1], color[0])
            cv2.circle(final_img, (x, y), radius, bgr, 3)
        title_text = self.title_input.text.strip()
        if title_text:
            cv2.putText(final_img, title_text, (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
        base_path = os.path.splitext(self.image_path)[0] + "_edit"
        image_path = base_path + ".png"
        txt_path = base_path + ".txt"
        # Preparar el texto de resultados
        counts = {cls["name"]: 0 for cls in CLASSES}
        for marker in self.scatter.markers:
            class_index = marker["class"]
            counts[CLASSES[class_index]["name"]] += 1
        total = sum(counts.values())
        results_text = "Resultados:\n"
        for cls_name, count in counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            results_text += f"{cls_name}: {count} ({percentage:.2f}%)\n"
        results_text += f"Total: {total}"
        
        if option == "both":
            cv2.imwrite(image_path, final_img)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(results_text)
            self.show_info("Guardado", f"Imagen y resultados guardados:\nImagen: {image_path}\nResultados: {txt_path}")
        elif option == "image":
            cv2.imwrite(image_path, final_img)
            self.show_info("Guardado", f"Imagen guardada en: {image_path}")
        elif option == "results":
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(results_text)
            self.show_info("Guardado", f"Resultados guardados en: {txt_path}")
        elif option == "whatsapp":
            # Guarda la imagen temporalmente y comparte usando plyer
            cv2.imwrite(image_path, final_img)
            try:
                from plyer import share
                share.share(title="Compartir vía WhatsApp", text=results_text, file_path=image_path)
            except Exception as e:
                self.show_info("Error", "No se pudo compartir vía WhatsApp.")

    def show_info(self, title, message):
        """
        Muestra un popup informativo.
        """
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()

if __name__ == '__main__':
    VisualTaggerApp().run()
