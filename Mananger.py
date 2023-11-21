import os
from File import File
import shutil


class FileManager:
    def __init__(self, root_folder_path, file_manager_ui=None):
        self.file_manager_ui = file_manager_ui
        self.root = File(os.path.basename(root_folder_path), root_folder_path)
        self.build_tree(root_folder_path, self.root, root_folder_path)

    def build_tree(self, path, parent_node, root_path):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                relative_path = os.path.relpath(item_path, root_path)
                is_folder = os.path.isdir(item_path)
                new_item = File(item, relative_path, is_folder)
                parent_node.child.append(new_item)
                if is_folder:
                    self.build_tree(item_path, new_item, root_path)
        except PermissionError as e:
            print(f"No hay permisos  '{path}'")


    def display_paths(self, node, current_path=""):
        if not node:
            return
        current_path = os.path.join(current_path, node.path)
        print(current_path)
        for child in node.child:
            self.display_paths(child, current_path)

    def find_node_by_name(self, item_name, node=None):
        if node is None:
            node = self.root

        if node.name == item_name:
            return node

        for child in node.child:
            result = self.find_node_by_name(item_name, child)
            if result is not None:
                return result

        return None
    

    def delete_item(self, item, node=None):
        if node is None:
            node = self.root

        for child in node.child:
            if child == item:
                try:
                    full_path = os.path.join(self.root.path, child.path)
                    if child.is_folder:
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                    node.child.remove(child)
                    return True
                except PermissionError as e:
                    print(f"No hay permisos para borrar '{item.name}'")
                    return False
            elif self.delete_item(item, child):
                return True

        return False


    def check_and_display_item(self, item_name):
        item_node = self.find_node_by_name(item_name)
        if item_node is not None:
            item_type = "carpeta" if item_node.is_folder else "archivo"
            print(f"El {item_type} '{item_name}' está presente.")
            print(f"Ruta: {os.path.join(self.root.path, item_node.path)}")
        else:
            print(f"El elemento '{item_name}' no se encuentra.")

            
    

    def add_item(self, parent_name, new_item_name):
        parent_node = self.find_node_by_name(parent_name)
        
        if parent_node:
            new_item_path = os.path.join(self.root.path, parent_node.path, new_item_name)
            new_item = File(new_item_name, os.path.relpath(new_item_path, self.root.path))

            try:
                with open(new_item_path, 'w') as new_file:
                    new_file.write("")  # Puedes agregar contenido inicial si es necesario

                parent_node.child.append(new_item)

                if new_item_name.endswith(".txt"):
                    new_item_path = os.path.join(self.root.path, parent_node.path, new_item_name)
                    # Llama al método en file_manager_ui si está disponible
                    if self.file_manager_ui:
                        self.file_manager_ui.edit_text_file(new_item_path)
                    return True
                else:
                    print(f"Se ha creado el {'archivo'} '{new_item_name}' en '{parent_name}'")
                    self.display_paths(self.root)  # Añade esta línea para imprimir la estructura actual del árbol
                    # Actualiza el árbol con la nueva información
                    return True
            except Exception as e:
                print(f"Error al crear el {'archivo'}: {e}")
                import traceback
                traceback.print_exc()  # Imprime la traza de la pila para obtener más detalles del error
                return False
        else:
            print(f"No se puede crear el {'archivo'}. '{parent_name}' no se encontró.")
            return False
        
    def add_folder(self, parent_name, new_folder_name):
        parent_node = self.find_node_by_name(parent_name)
        if parent_node:
            # Modificar para construir correctamente la ruta de la nueva carpeta
            new_folder_path = os.path.join(self.root.path, parent_node.path, new_folder_name)
            # Verificar si la carpeta ya existe en el disco antes de crearla
            if not os.path.exists(new_folder_path):
                os.mkdir(new_folder_path)
                new_folder = File(new_folder_name, os.path.relpath(new_folder_path, self.root.path))
                parent_node.child.append(new_folder)
                print(f"Se ha creado la carpeta '{new_folder_name}' en '{parent_name}'")
                # Actualiza la vista del árbol para reflejar la adición de la carpeta
                self.display_paths(self.root)
            else:
                print(f"La carpeta '{new_folder_name}' ya existe en '{parent_name}'")
        else:
            print(f"No se puede crear la carpeta. '{parent_name}' no se encontró.")

    def search_item_by_name(self, search_text, parent_node=None):
        if parent_node is None:
            parent_node = self.root

        search_results = []

        if parent_node.name.lower().startswith(search_text.lower()):
            # Si el nombre del nodo coincide, agregarlo a los resultados
            search_results.append(parent_node)

        for child in parent_node.child:
            # Realizar la búsqueda en los hijos recursivamente
            search_results.extend(self.search_item_by_name(search_text, child))

        return search_results


    def rename_item(self, old_name, new_name, node=None):
        if node is None:
            node = self.root

        for child in node.child:
            if child.name == old_name:
                old_item_path = os.path.join(self.root.path, child.path)
                new_item_path = os.path.join(self.root.path, os.path.dirname(child.path), new_name)

                try:
                    os.rename(old_item_path, new_item_path)
                except Exception as e:
                    print(f"Error al cambiar el nombre del {'carpeta' if child.is_folder else 'archivo'}: {e}")
                    return False

                child.name = new_name
                child.path = os.path.relpath(new_item_path, self.root.path).replace(os.sep, '/')
                self.update_paths(child, child.path)

                return True
            elif self.rename_item(old_name, new_name, child):
                return True

        return False


    def update_paths(self, node, parent_path):
    # Método para actualizar las rutas de los nodos hijos recursivamente
        for child in node.child:
            child.path = os.path.join(parent_path, child.name)
            if child.is_folder:
                self.update_paths(child, child.path)
                


# Uso de la clase FileManager
# root_folder_path = "/Users/juanm/Documents/Universidad/EstructuraDeDatos2/proyecto1/raiz"
# file_manager = FileManager(root_folder_path)

# Mostrar la ruta de cada carpeta dentro de la carpeta raíz
# file_manager.display_paths(file_manager.root)

#Eliminar una carpeta por su nombre de nodo
# folder_name_to_delete = "nodo3"
# file_manager.delete_folder_by_name(folder_name_to_delete)
# print("_____________________________")

#buscar por nombre si la carpeta e encuientra en a carpeta raiz
# folder_name_to_find = "nodo2"
# file_manager.check_and_display_folder(folder_name_to_find)

#Crear una nueva carpeta hija de una carpeta existente
# parent_folder_name = "raiz"
# new_folder_name = "nodo7"
# file_manager.add_folder(parent_folder_name, new_folder_name)

# Mostrar la ruta de cada carpeta después de agregar la nueva carpeta


