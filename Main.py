from File import File
import os
from Mananger import FileManager
import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog



class FileManagerUI:
    def __init__(self, root_folder_path, file_manager):
        self.root = tk.Tk()
        self.root.title("Administrador de Archivos")
        self.root.geometry("800x500")
        self.root.configure(borderwidth=5, relief="groove")

        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.container_buttons = ttk.Frame(self.main_container)
        self.container_buttons.pack(side=tk.TOP, pady=10)

        self.delete_button = tk.Button(self.container_buttons, text="Eliminar", command=self.delete_selected_item, bg="#FF6666", fg="black", font=("Arial", 9))
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.add_button = tk.Button(self.container_buttons, text="Agregar Carpeta", command=self.add_folder_prompt, bg="#66CC66", fg="black", font=("Arial", 9))
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.add_button = tk.Button(self.container_buttons, text="Agregar Archivo", command=self.add_item_prompt, bg="#66CC69", fg="black", font=("Arial", 9))
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.search_label = tk.Label(self.container_buttons, text="Buscar:")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(self.container_buttons, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = tk.Button(self.container_buttons, text="Buscar", command=self.search_item, bg="#66CCFF", fg="black", font=("Arial", 9))
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.rename_button = tk.Button(self.container_buttons, text="Cambiar Nombre", command=self.rename_folder_prompt, bg="#FFD700", fg="black", font=("Arial", 9))
        self.rename_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(self.container_buttons, text="Restablecer", command=self.reset_program, bg="#CCCCCC", fg="black", font=("Arial", 9))
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        
         # Inicializa self.edit_window
        self.edit_window = None

        self.tree = ttk.Treeview(self.main_container, selectmode='browse')
        self.tree.pack(side=tk.LEFT, fill=tk.Y)
        style = ttk.Style()
        style.configure("Treeview",
                        background="#E1E1E1",
                        fieldbackground="#E1E1E1",
                        foreground="black")

        style.map("Treeview",
                background=[("selected", "#347083")],
                foreground=[("selected", "white")])

        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.result_text = tk.Text(self.main_container, wrap=tk.WORD, height=10, width=50)
        self.result_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.show_item_contents)

        self.file_manager = file_manager
        self.build_tree(file_manager.root, "")

        self.result_text.bind("<Button-1>", lambda e: "break")
        self.result_text.bind("<KeyPress>", lambda e: "break")
        
        style.configure('folder', background='#E1E1E1', foreground='black')
        style.configure('file', background='#FFFFFF', foreground='black')

    def build_tree(self, node, parent_id, root_path=""):
        if not node:
            return
        item_id = self.tree.insert(parent_id, 'end', text=node.name, tags=('folder' if node.is_folder else 'file',))
        for child in node.child:
            child_path = os.path.join(root_path, child.path)
            self.build_tree(child, item_id, root_path)

            
    def delete_selected_item(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_name = self.tree.item(selected_item, 'text')
            item_node = self.file_manager.find_node_by_name(item_name)
            if item_node:
                self.file_manager.delete_item(item_node)
                self.tree.delete(selected_item)


    def add_item_prompt(self):
        selected_item = self.tree.selection()
        if selected_item:
            parent_name = self.tree.item(selected_item, 'text')
            parent_node = self.file_manager.find_node_by_name(parent_name)  # Asegúrate de obtener parent_node correctamente
            
            if parent_name:
                # Solicitar el nombre del nuevo elemento
                new_item_name = tk.simpledialog.askstring("Agregar Elemento", "Nombre del nuevo elemento:")

                if new_item_name:                
                    # Llamar al método de FileManager para agregar el elemento en la carpeta padre seleccionada
                    success = self.file_manager.add_item(parent_name, new_item_name)
                    
                    if success:
                        # Limpiar la vista del árbol antes de reconstruirlo
                        self.tree.delete(*self.tree.get_children())
                        
                        # Luego, actualiza la vista del árbol para reflejar la adición del elemento
                        self.build_tree(self.file_manager.root, '', self.file_manager.root.path)
                if new_item_name.endswith(".txt"):
                    new_item_path = os.path.join(self.file_manager.root.path, parent_node.path, new_item_name)
                    
                    # Si el nuevo elemento es un archivo de texto, abre la ventana de edición
                    self.edit_text_file(new_item_path)
                elif new_item_name:
                    # Si no es un archivo de texto, realiza la adición normal
                    success = self.file_manager.add_item(parent_name, new_item_name)
                    if success:
                        # Limpiar la vista del árbol antes de reconstruirlo
                        self.tree.delete(*self.tree.get_children())
                        # Luego, actualiza la vista del árbol para reflejar la adición del elemento
                    self.build_tree(self.file_manager.root, '', self.file_manager.root.path)  
        



    def add_folder_prompt(self):
        selected_item = self.tree.selection()
        parent_folder = self.tree.item(selected_item, 'text')

        if parent_folder:
            # Solicitar el nombre de la nueva carpeta
            new_folder_name = tk.simpledialog.askstring("Agregar Carpeta", "Nombre de la nueva carpeta:")

            if new_folder_name:
                # Llamar al método de FileManager para agregar la carpeta en la carpeta padre seleccionada
                self.file_manager.add_folder(parent_folder, new_folder_name)
                
                # Limpiar la vista del árbol antes de reconstruirlo
                self.tree.delete(*self.tree.get_children())
                
                # Luego, actualiza la vista del árbol para reflejar la adición de la carpeta
                parent_id = ""
                self.build_tree(self.file_manager.root, parent_id)
                
        
                    



    def show_item_contents(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_name = self.tree.item(selected_item, 'text')
            item_node = self.file_manager.find_node_by_name(item_name)
            if item_node:
                item_path = os.path.join(self.file_manager.root.path, item_node.path)
                content = self.get_content(item_path)
                self.update_result(content)

    def get_content(self, route):
        try:
            if os.path.isdir(route):
                content = os.listdir(route)
                return content
            else:
                # Si la ruta es un archivo, simplemente devuelve una lista con ese archivo
                return [os.path.basename(route)]
        except FileNotFoundError:
            return [f"La ruta {route} no existe."]
        except PermissionError:
            return [f"No tienes permisos para acceder a la ruta {route}."]


    def update_result(self, content):
        self.result_text.delete("1.0", tk.END)
        for element in content:
            self.result_text.insert(tk.END, f"{element}\n")

    def search_item(self):
        search_text = self.search_entry.get().strip()

        if search_text:
            selected_item = self.tree.selection()
            if selected_item:
                parent_node = self.file_manager.find_node_by_name(self.tree.item(selected_item, 'text'))
                self.tree.delete(*self.tree.get_children())
                search_results = self.file_manager.search_item_by_name(search_text, parent_node)
                parent_id = ""
                for result in search_results:
                    self.build_tree(result, parent_id)
                self.result_text.delete("1.0", tk.END)
                if search_results:
                    self.result_text.insert(tk.END, f"El elemento {result.name} se encuentra en el disco.\n")
                else:
                    self.result_text.insert(tk.END, f"El elemento {search_text} NO se encuentra en el disco.\n")
        else:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, "Por favor, ingrese un nombre para buscar.")
            parent_id = ""
            self.build_tree(self.file_manager.root, parent_id)
        
    def rename_folder_prompt(self):
        selected_item = self.tree.selection()

        if selected_item:
            old_folder_name = self.tree.item(selected_item, 'text')
            new_folder_name = tk.simpledialog.askstring("Cambiar Nombre de Carpeta", f"Nuevo nombre para '{old_folder_name}':")

            if new_folder_name:
                success = self.file_manager.rename_item(old_folder_name, new_folder_name)
                if success:
                    self.tree.delete(*self.tree.get_children())
                    self.build_tree(self.file_manager.root, "")
                else:
                    tk.messagebox.showinfo("Error", f"No se encontró la carpeta '{old_folder_name}'.")

    def reset_program(self):
        self.search_entry.delete(0, tk.END)
        self.tree.delete(*self.tree.get_children())
        self.build_tree(self.file_manager.root, "")
        self.result_text.delete("1.0", tk.END)
        
        
     #modificar el texto.txt   
    def edit_text_file(self, file_path):
         # Crea una nueva ventana para editar el archivo de texto
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title(f"Editar Archivo: {file_path}")

        text_widget = tk.Text(self.edit_window, wrap=tk.WORD, height=20, width=60)
        text_widget.pack(fill=tk.BOTH, expand=True)


        try:
            # Abre el archivo y carga su contenido en el widget de texto
            with open(file_path, 'r') as file:
                content = file.read()
                text_widget.insert(tk.END, content)
        except Exception as e:
            tk.messagebox.showinfo("Error", f"No se pudo abrir el archivo: {e}")

        save_button = tk.Button(self.edit_window, text="Guardar", command=lambda: self.save_text_file(file_path, text_widget))
        save_button.pack(pady=10)

    def save_text_file(self, file_path, text_widget):
        try:
            # Guarda el contenido del widget de texto de nuevo en el archivo
            with open(file_path, 'w') as file:
                file.write(text_widget.get("1.0", tk.END))
            tk.messagebox.showinfo("Guardado", "Archivo guardado exitosamente.")
            
            # Cierra la ventana de edición
            if self.edit_window:
                self.edit_window.destroy()
        except Exception as e:
            tk.messagebox.showinfo("Error", f"No se pudo guardar el archivo: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    root_folder_path = '/Users/juanm/Documents/Universidad/EstructuraDeDatos2/proyecto1/raiz'  # ruta de tu carpeta principal
    file_manager = FileManager(root_folder_path)
    file_manager_ui = FileManagerUI(root_folder_path, file_manager)
    file_manager_ui.run()


# root_folder_path = "/Users/juanm/Documents/Universidad/EstructuraDeDatos2/proyecto1/raiz"
# file_manager = FileManager(root_folder_path)

# # Mostrar la ruta de cada carpeta dentro de la carpeta raíz
# file_manager.display_paths(file_manager.root)


