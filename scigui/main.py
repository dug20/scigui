import tkinter as tk
import tkinter.filedialog
import tkinter.scrolledtext
from tkinter import ttk
import os.path
import json
import sys
import time 
import itertools 
import copy

# For matplotlib with tkinter
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from mpl_toolkits import mplot3d


# Functions for manipulating the 'active objects' and 'active functions' databases
def get_object(active_objects, iid):
    """Retrieve the item in a active_objects dictionary based on the IID.

    Args:
        active_objects (dict): Active objects dictionary
        iid (str): The IID, in the form \\First Folder\\Second Folder\\Object.

    Returns:
        dict or ObjectStore: The item stored at the given directory. It should reference the actual original item, so editing this result will edit the original.
    """
    key_list = iid.split("\\")
    key_list.pop(0)                                 # Index 0 is always just an empty string ('')

    # Make a copy of the dictionary, then iterate through it until we get what we want
    desired_object = active_objects

    for key in key_list:
        desired_object = desired_object[key]

    return desired_object

def set_object(database, iid, to_add):
    """
    Args:
        database (dict): active_objects
        iid (_type_): _description_
        to_add (_type_): thing to add
    """
    # Will either create a new set of subdictionaries to get to the desired iid, or will replace an existing object if there is one there
    key_list = iid.split("\\")
    key_list.pop(0)                                 # Index 0 is always just an empty string ('')

    iterated_dict = database

    # Get to the place we want to add the object
    for i in range(len(key_list) - 1):
        key = key_list[i]

        if not isinstance(iterated_dict, dict):
            raise ValueError("Attempted to create an object at {}, but the intermediate folder {} was already an existing object.".format(iid, key_list[i-1]))

        elif key in iterated_dict.keys():
            iterated_dict = iterated_dict[key]

        else:
            iterated_dict[key] = {}
            iterated_dict = iterated_dict[key]

    if not isinstance(iterated_dict, dict):
        raise ValueError("Attempted to create an object at {}, but the intermediate folder {} was already an existing object.".format(iid, key_list[-2]))

    if len(key_list) == 0:
        # This means we're just replacing the entire dictionary with a new one
        database.clear()
        for key, value in to_add.items():
            database[key] = value

    else:
        iterated_dict[key_list[-1]] = to_add

def move_object_in_dict(active_objects, old_iid, new_iid):
    """Move an object in an active_objects dictionary.

    Args:
        active_objects (dic): The active objects dictionary. This dictionary will be modified.
        old_iid (str): The IID of the original object that will be moved
        new_iid (str): The IID that you want the original object to have after being moved.
    """
    raise ValueError("Not yet implemented")

def get_function(active_functions, iid):
    return active_functions[iid.split("\\")[-1]]

def set_function(database, iid, to_add):
    """_summary_

    Args:
        database (dict): active_functions
        iid (_type_): _description_
        to_add (_type_): thing to add
    """
    database[iid.split("\\")[-1]] = to_add


# Functions related to Treeviews
def fill_objects_tree(treeview, dictionary, object_image, folder_image):
    # Note - this function does not check if there is an item in the Tree that needs to be removed (e.g. because they're absent in the dictionary).

    # Iterating function
    def add_dict_under_parent(dict_to_add, parent_key = ''):
        for key, value in dict_to_add.items():

            if "\\" in key:
                raise ValueError("Internal Objects Tree Error", "Objects cannot have '\\' in their name.")

            iid = parent_key + '\\' + key

            # If it's a dictionary (i.e. a folder), add it to the tree then add everything under it
            if isinstance(value, dict):

                # If an item already exists don't add it again
                if not treeview.exists(iid):
                    treeview.insert(parent_key, 'end', iid, text = key, image = folder_image)      # Parent ID, Position, ID, Displayed Text

                # But check everything under it for new items
                add_dict_under_parent(value, parent_key = iid)

            # If it's an object, just add it to the tree
            else:
                if not treeview.exists(iid):
                    treeview.insert(parent_key, 'end', iid, text = key, image = object_image)      

    add_dict_under_parent(dictionary)

def fill_functions_tree(treeview, dictionary, object_image = None, folder_image = None):
    """Placeholder function for filling a functions tree. It should work, but is very overkill since the functions tree shouldn't have folders or subfolders etc. Just a list of functions.
    """

    # Note - this function does not check if there is an item in the Tree that needs to be removed (e.g. because they're absent in the dictionary).

    # Iterating function
    def add_dict_under_parent(dict_to_add, parent_key = ''):
        for key, value in dict_to_add.items():

            if "\\" in key:
                raise ValueError("Internal Functions Tree Error", "Functions cannot have '\\' in their name.")

            iid = parent_key + '\\' + key

            # If it's a dictionary (i.e. a folder), add it to the tree then add everything under it
            if isinstance(value, dict):

                # If an item already exists don't add it again
                if not treeview.exists(iid):
                    treeview.insert(parent_key, 'end', iid, text = key)      # Parent ID, Position, ID, Displayed Text

                # But check everything under it for new items
                add_dict_under_parent(value, parent_key = iid)

            # If it's an object, just add it to the tree
            else:
                if not treeview.exists(iid):
                    treeview.insert(parent_key, 'end', iid, text = key)      

    add_dict_under_parent(dictionary)

def object_explorer(root, active_objects, variable_to_set, object_image, folder_image, object_type = None, grab_set = None):
        
        def on_close():
            toplevel.destroy()
            if not grab_set is None:
                grab_set.grab_set() 

        def select():
            if str(objects_tree.focus()) == '':
                tk.messagebox.showinfo("Select object error", "No object selected from the tree.", parent = toplevel)
                
            else:
                iid = str(objects_tree.focus())
                 
                # If there's no preference on the object type, just select it
                if object_type == None:
                    variable_to_set.set(iid)
                    toplevel.destroy()
                    if not grab_set is None:
                        grab_set.grab_set() 

                # If there is preference on object type, we must check what the user selected
                else:
                    selected_object = get_object(active_objects, iid)

                    # Check what datatype the object is
                    if type(selected_object) is ObjectStore:

                        if not isinstance(selected_object.get_object(), object_type):
                            tk.messagebox.showinfo("Select object error", 
                                                   f"Object selected is the wrong type. It must be of type '{object_type.__name__}'. You selected '{type(selected_object.get_object()).__name__}'.", 
                                                   parent = toplevel)
                        
                        else:
                            variable_to_set.set(iid)
                            toplevel.destroy()
                            if not grab_set is None:
                                grab_set.grab_set() 
                                
                    # This code likely only gets executed if a folder has been selected.
                    else:
                        if not isinstance(selected_object.get_object(), object_type):
                            tk.messagebox.showinfo("Select object error", 
                                                   f"Object selected is the wrong type. It must be of type '{object_type.__name__}'. You selected '{object_type.__name__, type(selected_object).__name__}'.", 
                                                   parent = toplevel)
                        
                        else:
                            variable_to_set.set(iid)
                            toplevel.destroy()
                            if not grab_set is None:
                                grab_set.grab_set() 
        
        toplevel = tk.Toplevel(root)
        toplevel.protocol("WM_DELETE_WINDOW", on_close)
        toplevel.grab_set()

        objects_tree = ttk.Treeview(toplevel, show = "tree", selectmode = "browse") # show = 'tree' will remove the header bar, and #selectmode = "browse" means only one object can be selected at a time
        objects_tree.pack(side = "left")

        fill_objects_tree(objects_tree, active_objects, object_image = object_image, folder_image = folder_image)

        select_button = tk.Button(toplevel, text = "Select", command = lambda : select())
        select_button.pack(side = "right")



# Generic GUI functions
def open_popup(root, title_text, body_text):
    # Placeholder - this used to be an old function
    tk.messagebox.showinfo(title_text, body_text, parent = root)

def raise_above_all(window):
    window.attributes('-topmost', 1)
    window.attributes('-topmost', 0)

class SortableCombobox(ttk.Combobox):
    # Credit to Autiwa from Stackoverflow for this key-press-to-jump Combobox
    # https://stackoverflow.com/questions/53848622/how-to-bind-keypress-event-for-combobox-drop-out-menu-in-tkinter-python-3-7

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pd = self.tk.call('ttk::combobox::PopdownWindow', self) #get popdownWindow reference 
        lb = pd + '.f.l' #get popdown listbox
        self._bind(('bind', lb),"<KeyPress>",self.popup_key_pressed,None)

    def popup_key_pressed(self,evt):
        values = self.cget("values")
        for i in itertools.chain(range(self.current() + 1,len(values)),range(0,self.current())):
            if evt.char.lower() == values[i][0].lower():
                self.current(i)
                self.icursor(i)
                self.tk.eval(evt.widget + ' selection clear 0 end') #clear current selection
                self.tk.eval(evt.widget + ' selection set ' + str(i)) #select new element
                self.tk.eval(evt.widget + ' see ' + str(i)) #spin combobox popdown for selected element will be visible
                return



class String(str):
    """This is a class for storing 'raw' user inputs, i.e. just a string."""
    def __new__(self, dictionary):
        instance = super().__new__(self, dictionary["Value"])
        return instance

    @staticmethod
    def inputs():
        return {"Value" : "raw"} 

class ObjectStore:
    def __init__(self, application, index, dictionary):
        self.application = application
        self.object_index = index
        self.objects_list = application.objects
        self.object = self.objects_list[index]
        self.dictionary = dictionary

    @property
    def index(self):
        return self.object_index

    def __repr__(self):
        return "<ObjectStore>(" + str(self.dictionary) + ")"

    def get_object(self):
        altered_dictionary = self.dictionary.copy()

        # If there are any references to objects, replace the directory to the object with the object itself
        for key, value in self.object.inputs().items():
            if value == "object":
                altered_dictionary["\\INPUTS\\"][key] = get_object(active_objects = self.application.active_objects, iid = self.dictionary[key])  # This will retrieve an "ObjectStore" object
                altered_dictionary["\\INPUTS\\"][key] = altered_dictionary["\\INPUTS\\"][key].get_object()                                                          # This converts the "ObjectStore" object to the actual object itself.

            if value == "raw" and ("\\" in str(altered_dictionary["\\INPUTS\\"][key])):
                # Get the actual 'String' object if it's a reference to an object - check this by looking for '\\' in the user's input
                altered_dictionary["\\INPUTS\\"][key] = get_object(active_objects = self.application.active_objects, iid = self.dictionary["\\INPUTS\\"][key])  # This will retrieve an "ObjectStore" object
                altered_dictionary["\\INPUTS\\"][key] = altered_dictionary["\\INPUTS\\"][key].get_object()                                                          # This converts the "ObjectStore" object to the actual object itself.

        return self.object(dictionary = altered_dictionary["\\INPUTS\\"])

    def to_json_form(self):
        # For saving to a .json file
        dictionary = self.dictionary
        dictionary["\\OBJECT_INDEX\\"] = self.object_index

        return dictionary

    @staticmethod
    def from_json_form(application, dict_from_json):
        object_index = dict_from_json["\\OBJECT_INDEX\\"]
        dictionary = dict_from_json.copy()
        del dictionary["\\OBJECT_INDEX\\"]

        return ObjectStore(application = application, index = object_index, dictionary = dictionary)

    @staticmethod
    def check_if_json_form(dict):
        if "\\OBJECT_INDEX\\" in dict.keys():
            return True
        else:
            return False

class FunctionStore:
    def __init__(self, application, index, dictionary):

        self.application = application
        self.function_index = index
        self.functions_list = application.functions
        self.function = self.functions_list[index]
        self.dictionary = dictionary

    @property
    def index(self):
        return self.function_index

    def __repr__(self):

        return "<FunctionStore>(" + str(self.dictionary) + ")"

    def execute(self):

        # Edit the inputs dictionary so it replaces any references to objects with the actual object
        inputs_dict = copy.deepcopy(self.dictionary["\\INPUTS\\"])

        # Provide a reference to the application, so the user can do their own GUI stuff if they want
        inputs_dict["\\APPLICATION\\"] = self.application

        # If there are any references to objects, replace the directory to the object with the object itself
        for key, value in self.function.inputs().items():

            if isinstance(value, list):
                if value[0] == "object":
                    for i in range(len(inputs_dict[key])):

                        try:
                            inputs_dict[key][i] = get_object(active_objects = self.application.active_objects, iid = inputs_dict[key][i])     # This will retrieve an "ObjectStore" object
                            inputs_dict[key][i] = inputs_dict[key][i].get_object()          
                                                                                            # This converts the "ObjectStore" object to the actual object itself.
                        except KeyError:
                            open_popup(self.application.root, "Object link error", f"Could not find object located at {object_location} for input {key} when executing function.")


            elif callable(value):
                actual_datatype = value(inputs_dict)

                if actual_datatype == "object":
                    try:
                        inputs_dict[key] = get_object(active_objects = self.application.active_objects, iid = self.dictionary["\\INPUTS\\"][key])     # This will retrieve an "ObjectStore" object
                        inputs_dict[key] = inputs_dict[key].get_object()          
                                                                                        # This converts the "ObjectStore" object to the actual object itself.

                    except KeyError:
                        open_popup(self.application.root, "Object link error", f"Could not find object located at {object_location} for input {key} when executing function.")


            elif value == "object":
                try:
                    inputs_dict[key] = get_object(active_objects = self.application.active_objects, iid = self.dictionary["\\INPUTS\\"][key])     # This will retrieve an "ObjectStore" object
                    inputs_dict[key] = inputs_dict[key].get_object()          
                                                                                      # This converts the "ObjectStore" object to the actual object itself.
                except KeyError:
                    open_popup(self.application.root, "Object link error", f"Could not find object located at {object_location} for input {key} when executing function.")


            elif value == "raw" and ("\\" in str(inputs_dict[key])):
                # Get the actual 'String' object if it's a reference to an object - check this by looking for '\\' in the user's input
                try:
                    inputs_dict[key] = get_object(active_objects = self.application.active_objects, iid = self.dictionary["\\INPUTS\\"][key])     # This will retrieve an "ObjectStore" object
                    inputs_dict[key] = inputs_dict[key].get_object()                                                                            # This converts the "ObjectStore" object to the actual object itself.

                except KeyError:
                    object_location = self.dictionary['\\INPUTS\\'][key]
                    open_popup(self.application.root, "Object link error", f"Could not find object located at {object_location} for input {key} when executing function.")

        # Execute the function
        results = self.function.execute(inputs_dictionary = inputs_dict, outputs_dictionary = self.dictionary["\\OUTPUTS\\"].copy())

        # Now set the output objects
        updated_objects = False
        for key, value in self.dictionary["\\OUTPUTS\\"].items():
            
            # If the user leaves a blank entry for the output, don't save anything
            if self.dictionary["\\OUTPUTS\\"][key] == "":
                pass

            else:
                object_type = self.function.outputs()[key]

                # Find the object index for the object type we are going to produce. NOTE THAT THIS IS DONE BY COMPARING THEIR NAMES!
                object_index = None
                for i in range(len(self.application.objects)):
                    if object_type.__name__ == self.application.objects[i].__name__:
                        object_index = i
                
                if object_index == None:
                    raise ValueError("Failed to find the object of type {} in the list of objects available in the application".format(object_type))

                # Add the object to our active_objects dictionary
                object_store_to_add = ObjectStore(application = self.application, index = object_index, dictionary = {"\\INPUTS\\" : results[key]})

                set_object(database = self.application.active_objects, iid = self.dictionary["\\OUTPUTS\\"][key], to_add = object_store_to_add)
                updated_objects = True
        
        if updated_objects:
            # Refresh the objects tree
            self.application.objects_tree.delete(*self.application.objects_tree.get_children())
            fill_objects_tree(treeview = self.application.objects_tree, dictionary = self.application.active_objects, object_image = self.application.object_image, folder_image = self.application.folder_image)

    def to_json_form(self):
        # For saving to a .json file
        dictionary = self.dictionary
        dictionary["\\FUNCTION_INDEX\\"] = self.function_index

        return dictionary

    @staticmethod
    def from_json_form(application, dict_from_json):
        function_index = dict_from_json["\\FUNCTION_INDEX\\"]
        dictionary = dict_from_json.copy()
        del dictionary["\\FUNCTION_INDEX\\"]

        return FunctionStore(application = application, index = function_index, dictionary = dictionary)

    @staticmethod
    def check_if_json_form(dict):
        if "\\FUNCTION_INDEX\\" in dict.keys():
            return True
        else:
            return False



class TextRedirector():
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, string):       
        self.textbox.configure(state = "normal")        # Make textbox editable

        # Add text in a new line
        if string == "\n" or string == "":
            # Python prints a new line string on top of whatever the user prints. Don't add the time stamp to this.
            self.textbox.insert("end", string)                 
        else:
            current_time = str(time.strftime("%H:%M:%S", time.localtime()))
            self.textbox.insert("end", f"[{current_time}] {string}")

        self.textbox.see("end")                         # Scroll to end
        self.textbox.configure(state = "disabled")      # Make textbox read only

    def flush(self):
        pass

class ToolTip():
    # Credit to squareRoot17 for most of this code in their StackOverflow answer:
    # https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        # Display text in a little pop up
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify="left",
                      background="#ffffe0", relief="solid", borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tool_tip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)



class Application:
    def __init__(self, objects, functions):
        # Get the actual location of the script, so we can import the icons for objects and folder
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        # Initialisation
        self.objects = [String] + objects
        self.functions = functions
        self.open_file = None
        self.modified_and_not_saved = False

        # Main window
        self.root = tk.Tk()
        self.root.geometry("600x400")   # So if you un-maximise it goes back to this size
        self.root.state('zoomed')       # Initialise as maximised
        self.root.title('SciGUI')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)      # Run custom function when user tries to click 'x'
        self.root.bind('<Control-s>', lambda info: self.save())      # Quick save shortcut

        self.root.bind("<Unmap>", self.hide_all)  # Hide all toplevels when the main window is minimised
        self.root.bind("<Map>", self.show_all)    # Show all toplevels when the main window is reopened

        # Current list of objects and functions the user has added
        self.active_objects = {}
        self.active_functions = {}

        # Menu with 'file', etc...
        self.root_menubar = tk.Menu(self.root)
        self.root.config(menu = self.root_menubar)

        # File menu dropdown
        self.file_menu = tk.Menu(tearoff = "off")
        self.file_menu.add_command(label = 'New', command = lambda : self.new())
        self.file_menu.add_command(label = 'Open', command = lambda : self.open())
        self.file_menu.add_command(label = 'Save', command = lambda : self.save(), accelerator = "Ctrl+S")
        self.file_menu.add_command(label = 'Save as', command = lambda : self.save_as())
        
        # Edit menu dropdown
        self.edit_menu = tk.Menu(tearoff = "off")
        self.edit_menu.add_command(label = 'Clear all objects', command = lambda : self.clear_all_objects())
        self.edit_menu.add_command(label = 'Clear all functions', command = lambda : self.clear_all_functions())

        # Function menu dropdown
        self.functions_menu = tk.Menu(tearoff = "off")
        self.functions_menu.add_command(label = 'Run all', command = lambda : self.run_all_functions())

        # 'Help' menu dropdown
        self.help_menu = tk.Menu(tearoff = "off")

        self.debug_menu = tk.Menu(tearoff = "off")
        self.debug_menu.add_command(label = 'Clear console', command = lambda : self.clear_console())
        self.debug_menu.add_command(label = 'Print active objects', command = lambda : print(self.active_objects))
        self.debug_menu.add_command(label = 'Print active functions', command = lambda : print(self.active_functions))
        self.debug_menu.add_command(label = 'Print objects Treeview', command = lambda : self.print_objects_treeview())

        self.help_menu.add_cascade(label = 'Debug', menu = self.debug_menu)

        # Add the relevant cascades to the main menu at the top
        self.root_menubar.add_cascade(label = "File", menu = self.file_menu)
        self.root_menubar.add_cascade(label = "Edit", menu = self.edit_menu)
        self.root_menubar.add_cascade(label = "Functions", menu = self.functions_menu)
        self.root_menubar.add_cascade(label = "Help", menu = self.help_menu)



        # Tabs with 'Objects' and 'Functions'
        self.root_notebook = ttk.Notebook(self.root)
        
        objects_tab = ttk.Frame(self.root_notebook)
        functions_tab = ttk.Frame(self.root_notebook)

        self.root_notebook.add(objects_tab, text ='Objects')
        self.root_notebook.add(functions_tab, text ='Functions')
        self.root_notebook.pack(side = "left", fill = "y")

        self.object_image = tk.PhotoImage(file = os.path.join(__location__, "img\\object.gif"))
        self.folder_image = tk.PhotoImage(file = os.path.join(__location__, "img\\folder.gif"))



        # Console print out
        self.console_widget = tk.scrolledtext.ScrolledText(self.root, height = 4, font = ("consolas", "8", "normal"))
        self.console_widget.pack(side = "bottom", fill = "both")
        self.console_widget.configure(state = "disabled")                                          # Make textbox read only
        sys.stdout = TextRedirector(self.console_widget)
        


        # Objects tree
        self.objects_tree = ttk.Treeview(objects_tab, show = "tree", selectmode = "browse") # show = 'tree' will remove the header bar, and #selectmode = "browse" means only one object can be selected at a time
        self.objects_tree.pack(fill = "y", expand = True)
        self.objects_tree_rmb = tk.Menu(self.objects_tree, tearoff = 0)
        self.add_object_menu = tk.Menu(self.objects_tree_rmb, tearoff = 0)

        # Set up the RMB options
        self.objects_tree_rmb.add_cascade(label = "Add object", menu = self.add_object_menu)

        for i in range(len(self.objects)):
            object = self.objects[i]
            self.add_object_menu.add_command(label = str(object.__name__), command = lambda i = i: self.obj_fnc_window("object", i))

        self.objects_tree_rmb.add_command(label = "Add folder", command = lambda : self.add_folder())
        self.added_extra_object_menu_options = False

        def objects_tree_left_click(event):
            self.selected_object_x = event.x_root
            self.selected_object_y = event.y_root

            # Select the object you right clicked on
            iid = self.objects_tree.identify_row(event.y)
            if iid:
                self.objects_tree.selection_set(iid)   
                self.objects_tree.focus(iid)

            # Or clear selection if no item was chosen    
            else:
                for item in self.objects_tree.selection():
                    self.objects_tree.selection_remove(item)
                    self.objects_tree.focus('')

        def objects_tree_right_click(event):
            objects_tree_left_click(event)

            try:
                # Check if we've selected an object, if so we can display the "Rename" and "Delete" options
                if str(self.objects_tree.focus()) != '' and not self.added_extra_object_menu_options:
                    self.objects_tree_rmb.add_command(label = "Edit", command = lambda : self.obj_fnc_window("object"))
                    self.objects_tree_rmb.add_command(label = "Delete", command = lambda : self.delete_object())
                    self.added_extra_object_menu_options = True

                elif str(self.objects_tree.focus()) == '' and self.added_extra_object_menu_options:
                    self.objects_tree_rmb.delete(2,3)
                    self.added_extra_object_menu_options = False
                
                # Display the right click menu
                self.objects_tree_rmb.tk_popup(event.x_root, event.y_root)

            finally:
                self.objects_tree_rmb.grab_release()

        def objects_tree_double_click(event):
            # Check if we've selected an object, if so then edit it upon double click
            if str(self.objects_tree.focus()) != '':
                # Only edit if it's not a folder. If we double click a folder, just open it up
                if not isinstance(get_object(self.active_objects, self.objects_tree.focus()), dict):
                    self.obj_fnc_window("object")

        self.objects_tree.bind("<Button-3>", objects_tree_right_click)
        self.objects_tree.bind("<Button-1>", objects_tree_left_click)
        self.objects_tree.bind("<B1-Motion>", self.move_object_drag, add = '+') 
        self.objects_tree.bind("<ButtonRelease-1>", self.move_object_release)
        self.objects_tree.bind('<Double-Button-1>', objects_tree_double_click)
        self.moving_object = False

        # Functions tree
        self.functions_tree = ttk.Treeview(functions_tab, show = "tree", selectmode = "browse")
        self.functions_tree.pack(fill = "y", expand = True)

        self.functions_tree_rmb = tk.Menu(self.functions_tree, tearoff = 0)
        self.add_function_menu = tk.Menu(self.functions_tree_rmb, tearoff = 0)

        # Set up the RMB options
        self.functions_tree_rmb.add_cascade(label = "Add function", menu = self.add_function_menu)

        for i in range(len(self.functions)):
            function = self.functions[i]
            self.add_function_menu.add_command(label = str(function.__name__), command = lambda i = i: self.obj_fnc_window("function", i))
        
        self.added_extra_function_menu_options = False

        def functions_tree_left_click(event):
            # Select the object you right clicked on
            iid = self.functions_tree.identify_row(event.y)
            if iid:
                self.functions_tree.selection_set(iid)   
                self.functions_tree.focus(iid)

            # Or clear selection if no item was chosen    
            else:
                for item in self.functions_tree.selection():
                    self.functions_tree.selection_remove(item)
                    self.functions_tree.focus('')

        def functions_tree_right_click(event):
            functions_tree_left_click(event)

            try:
                # Check if we've selected an object, if so we can display the "Rename" and "Delete" options
                if str(self.functions_tree.focus()) != '' and not self.added_extra_function_menu_options:
                    self.functions_tree_rmb.add_command(label = "Execute", command = lambda : self.execute_function())
                    self.functions_tree_rmb.add_command(label = "Edit", command = lambda : self.obj_fnc_window("function"))
                    self.functions_tree_rmb.add_command(label = "Delete", command = lambda : self.delete_function())
                    self.added_extra_function_menu_options = True

                elif str(self.functions_tree.focus()) == '' and self.added_extra_function_menu_options:
                    self.functions_tree_rmb.delete(1,4)
                    self.added_extra_function_menu_options = False
                
                # Display the right click menu
                self.functions_tree_rmb.tk_popup(event.x_root, event.y_root)

            finally:
                self.functions_tree_rmb.grab_release()

        def functions_tree_double_click(event):
            # Check if we've selected an object, if so then edit it upon double click
            if str(self.functions_tree.focus()) != '':
                self.obj_fnc_window("function")

        self.functions_tree.bind("<Button-3>", functions_tree_right_click)
        self.functions_tree.bind("<Button-1>", functions_tree_left_click)
        self.functions_tree.bind("<B1-Motion>", self.move_function, add = '+') 
        self.functions_tree.bind('<Double-Button-1>', functions_tree_double_click)


        # Initialise data
        functions = {}
        objects = {}



    def run(self):
        self.root.mainloop()

    def hide_all(self, event):
        for child in self.root.children.values():
            if isinstance(child, tk.Toplevel):
                child.withdraw() 

    def show_all(self, event):
        for child in self.root.children.values():
            if isinstance(child, tk.Toplevel):
                child.deiconify() 


    def on_closing(self):
        if self.modified_and_not_saved:
            if tk.messagebox.askyesno("Quit", "File not saved, do you still want to quit?"):
                self.root.destroy()
        
        else:
            self.root.destroy()


    def new(self):
        def proceed():
            self.clear_all_objects(popup = False)
            self.clear_all_functions(popup = False)
            self.open_file = None
            self.modified_and_not_saved = False
        
        if self.modified_and_not_saved:
            if tk.messagebox.askyesno("Modified program", "File unsaved since last modification, still proceed?"):
                proceed()

        else:
            proceed()

    def load_file(self, filename, refresh_treeviews = True, print_msg = True):
        # Convert file to dictionary
        with open(filename) as f:
            json_opened = json.load(f)
        
        # Convert the dictionary-stored objects and functions to ObjectStore and FunctionStore objects
        def convert_to_stores(dict):

            for key in dict.keys():

                if ObjectStore.check_if_json_form(dict[key]):
                    dict[key] = ObjectStore.from_json_form(application = self, dict_from_json = dict[key])

                elif FunctionStore.check_if_json_form(dict[key]):
                    dict[key] = FunctionStore.from_json_form(application = self, dict_from_json = dict[key])

                else:
                    convert_to_stores(dict[key])
        
        convert_to_stores(json_opened)

        # Overwrite our active functions and active objects
        self.active_objects = json_opened["Objects"].copy()
        self.active_functions = json_opened["Functions"].copy()
        
        if refresh_treeviews:
            # Re-render the TreeViews
            self.objects_tree.delete(*self.objects_tree.get_children())
            self.functions_tree.delete(*self.functions_tree.get_children())

            fill_objects_tree(treeview = self.objects_tree, dictionary = self.active_objects, object_image = self.object_image, folder_image = self.folder_image)
            fill_functions_tree(treeview = self.functions_tree, dictionary = self.active_functions)

        # Keep track of which file we opened
        self.open_file = filename

        if print_msg:
            print(f"Loaded file {self.open_file}")

    def save_file(self, filename):
        # Get the dict we want to save
        save_dict = {"Objects" : self.active_objects.copy(), "Functions" : self.active_functions.copy()}

        # Go through the dictionary, and convert any ObjectStore or FunctionStore objects to their dictionary forms
        def convert_stores(dict):
            for key in dict.keys():
                if isinstance(dict[key], ObjectStore) or isinstance(dict[key], FunctionStore):
                    dict[key] = dict[key].to_json_form()
            
                else:
                    convert_stores(dict[key])

        convert_stores(save_dict)

        # Save to a .json file
        with open(filename, 'w') as fp:
            json.dump(save_dict, fp)
        
        # Load the .json file we saved (this is a bit inefficient, but a placeholder due to issues with trying to make a deepcopy of active_objects)
        self.load_file(filename, refresh_treeviews = False, print_msg = False)

        print("Saved to {}".format(filename))

        self.modified_and_not_saved = False

    def open(self):
        if self.modified_and_not_saved:
            if tk.messagebox.askyesno("Open file", "Program not saved, do you still want to open a new file?"):
                proceed = True
        else:
            proceed = True
            
        if proceed:
            # Open a .json file
            if self.open_file == None:
                initialdir = "/"
            else:
                initialdir = self.open_file
            
            filename = tk.filedialog.askopenfilename(initialdir = initialdir,
                                                        title = "Open file",
                                                        filetypes = [('SciGUI Files', '*.sgui'), ('JSON Files', '*.json'), ('All Files', '*.*')])
            
            if filename == '':
                pass

            else:
                self.load_file(filename)

    def save(self):
        # Save to the currently open .json file
        if self.open_file == None:
            self.save_as()

        else:
            self.save_file(self.open_file)

    def save_as(self):
        if self.open_file == None:
            initialdir = "/"
        else:
            initialdir = self.open_file

        filename = tk.filedialog.asksaveasfile(initialdir = initialdir, title = "Save as", filetypes = [('SciGUI Files', '*.sgui')], defaultextension = ".sgui")
        
        if filename == None:
            # This occurs if the user clicked cancel
            pass

        else:
            filename = filename.name
            self.save_file(filename)



    def popup(self, title_text, body_text):
        """Open a popup. This can be called from a user's function by manipulating the \\APPLICATION\\ key.

        Args:
            title_text (str): The text to appear in the title.
            body_text (str): The text to appear in the body

        """
        open_popup(self.root, title_text = title_text, body_text = body_text)



    def clear_all_objects(self, popup = True):

        def proceed():
            self.objects_tree.delete(*self.objects_tree.get_children())
            self.active_objects = {}

        if popup:
            self.yes_no_popup("Clear all objects", "Are you sure you want to clear all objects?", lambda : proceed(), default = "No")

        else:
            proceed()

    def clear_all_functions(self, popup = True):

        def proceed():
            self.functions_tree.delete(*self.functions_tree.get_children())
            self.active_functions = {}
        
        if popup:
            self.yes_no_popup("Clear all functions", "Are you sure you want to clear all functions?", lambda : proceed(), default = "No")

        else:
            proceed()

    def clear_console(self):
        self.console_widget.configure(state = 'normal')
        self.console_widget.delete('1.0', 'end')
        self.console_widget.configure(state = 'disabled')

    def print_objects_treeview(self):

        def print_children(parent):
            
            print(parent)

            for child in self.objects_tree.get_children(parent):
                print_children(child)

        print_children('')

    def move_object_drag(self, event):
        treeview = event.widget
        moveto_iid = str(treeview.identify_row(event.y))
        moveto_parent_iid = str(treeview.parent(moveto_iid))

        try: 
            self.original_item_iid = str(treeview.selection()[0])
            self.original_parent_iid = str(treeview.parent(self.original_item_iid))
            self.original_item_index = treeview.index(self.original_item_iid) 

            self.moving_object = True
            self.root.config(cursor = "fleur")

        except IndexError:
            # If there are no items
            self.original_item_iid = ''
            self.original_parent_iid = ''
            self.original_item_index = 0

        # Set moveto_index based on mouse position
        if moveto_iid == "":

            if event.y_root > self.selected_object_y:
                # Move down if we move below the treeview
                moveto_index = self.original_item_index + 2

            elif event.y_root < self.selected_object_y:
                # Move up if we move above the treeview
                moveto_index = self.original_item_index - 2

        else:
            moveto_index = treeview.index(moveto_iid)  

        if ( (moveto_parent_iid == self.original_parent_iid or moveto_iid == "")         # Only move within the same folder. Or if our mouse is outside the treeview.
            and abs(self.original_item_index - moveto_index) > 1                         # Must move past an object before moving to its position
            and self.original_item_iid != ""                                             # Removes error when nothing is selected
            and event.x_root < treeview.winfo_rootx() + treeview.winfo_width()      # Don't do anything if mouse is to the left or right of the treeview
            and event.x_root > treeview.winfo_rootx()):

            # Note this is all done immediately - it doesn't wait for LMB release

            # Visually rearrange treeview
            index_to_actually_move_to = self.original_item_index + round(0.5*(moveto_index - self.original_item_index))
            treeview.move(self.original_item_iid, self.original_parent_iid, index_to_actually_move_to)   

            # Get the new order of the dictionary keys
            iid_list = treeview.get_children(self.original_parent_iid)
            key_list = [None] * len(iid_list)

            for i in range(len(iid_list)):
                key_list[i] = iid_list[i].split("\\")[-1]
            
            # Recreate the dictionary in the correct order
            original_dict = get_object(active_objects = self.active_objects, iid = self.original_parent_iid)
            new_dict = {}

            for key in key_list:
                new_dict[key] = original_dict[key]

            set_object(database = self.active_objects, iid = self.original_parent_iid, to_add = new_dict)

            self.modified_and_not_saved = True

        # The if statements below just modify the cursor to indicate what will happen when move_object_release() is executed
        if (moveto_iid == ""                                                          
            and self.original_parent_iid != ""                                         
            and event.y_root > self.selected_object_y                                  
            and event.x_root < treeview.winfo_rootx() + treeview.winfo_width()       
            and event.x_root > treeview.winfo_rootx()):                                

            self.root.config(cursor = "@scigui/img/add_to_folder.cur")

        elif (moveto_iid != "" 
                and isinstance(get_object(self.active_objects, moveto_iid), dict)     
                and self.original_item_iid not in moveto_iid                          
                and self.original_parent_iid != moveto_iid):                        
            self.root.config(cursor = "@scigui/img/add_to_folder.cur")

        elif (not isinstance(get_object(self.active_objects, moveto_iid), dict)     
                and self.original_parent_iid != moveto_parent_iid):   
            self.root.config(cursor = "@scigui/img/add_under.cur")               
            

    def move_object_release(self, event):

        if self.moving_object:

            # Should make this do the 'move into folder' action. So moving into a folder only occurs if you release the LMB, whilst hovering over a folder
            treeview = event.widget
            moveto_iid = str(treeview.identify_row(event.y))
            moveto_parent_iid = str(treeview.parent(moveto_iid))

            if (moveto_iid == ""                                                            # Released without hovering over any of the existing objects
                and self.original_parent_iid != ""                                          # Object wasn't already in the top level folder
                and event.y_root > self.selected_object_y                                   # If we're below the existing object
                and event.x_root < treeview.winfo_rootx() + treeview.winfo_width()          # And we're still within the Treeview (in the x-direction)
                and event.x_root > treeview.winfo_rootx()):                                 # I.e. the mouse was released below all the existing objects

                #print("MOVE TO TOP LEVEL")
              
                # Delete item from old position, and add it to the top
                key = self.original_item_iid.split("\\")[-1]
                original_parent = get_object(active_objects = self.active_objects, iid = self.original_parent_iid)

                if key in self.active_objects.keys():
                    self.popup("Move Object Error", "Cannot move this object into the new folder, it already has an item in it with the same name.")
                    self.root.config(cursor = "arrow")
                    self.moving_object = False
                    return

                self.active_objects[key] = original_parent[key]
                del original_parent[key]

                # Delete the old object and re-render the treeview (we can't just move the objects around - the IIDs need to change due to the folder change)
                treeview.delete(self.original_item_iid)
                fill_objects_tree(treeview, self.active_objects, self.object_image, self.folder_image)
                self.modified_and_not_saved = True
                
            elif (moveto_iid != "" 
                  and isinstance(get_object(self.active_objects, moveto_iid), dict)     # Folder selected
                  and self.original_item_iid not in moveto_iid                          # Folder is not within the original object being moved
                  and self.original_parent_iid != moveto_iid):                          # Not moving to the folder it's already in

                #print("MOVE TO BOTTOM OF FOLDER")
                
                # Delete item from old folder, add it to the new folder
                key = self.original_item_iid.split("\\")[-1]
                original_parent = get_object(active_objects = self.active_objects, iid = self.original_parent_iid)
                new_parent = get_object(active_objects = self.active_objects, iid = moveto_iid)

                if key in new_parent.keys():
                    self.popup("Move Object Error", "Cannot move this object into the new folder, it already has an item in it with the same name.")
                    self.root.config(cursor = "arrow")
                    self.moving_object = False
                    return

                new_parent[key] = original_parent[key]
                del original_parent[key]

                # Delete the old object and re-render the treeview (we can't just move the objects around - the IIDs need to change due to the folder change)
                treeview.delete(self.original_item_iid)
                fill_objects_tree(treeview, self.active_objects, self.object_image, self.folder_image)
                self.modified_and_not_saved = True

            elif (not isinstance(get_object(self.active_objects, moveto_iid), dict)     # Object selected
                  and self.original_parent_iid != moveto_parent_iid):                   # Object is in a different folder to the one being moved

                #print("MOVE BELOW OBJECT")

                # Check if an item with the same name exists in the folder we want to move to
                key = self.original_item_iid.split("\\")[-1]
                new_parent = get_object(active_objects = self.active_objects, iid = moveto_parent_iid)

                if key in new_parent.keys():
                    self.popup("Move Object Error", "Cannot move this object into the new folder, it already has an item in it with the same name.")
                    self.root.config(cursor = "arrow")
                    self.moving_object = False
                    return

                # Get the list of things we want in the target folder
                moveto_index = treeview.index(moveto_iid)
                iid_list = list(treeview.get_children(moveto_parent_iid))
                iid_list.insert(moveto_index + 1, self.original_item_iid)           # Insert where we want the new item
                key_list = [None] * len(iid_list)

                for i in range(len(iid_list)):
                    key_list[i] = iid_list[i].split("\\")[-1]

                old_moveto_parent = get_object(active_objects = self.active_objects, iid = moveto_parent_iid)
                new_moveto_parent = {}

                for key in key_list:
                    if key in old_moveto_parent.keys():
                        # Add the original items
                        new_moveto_parent[key] = old_moveto_parent[key]

                    else:
                        # Add the new item at the right position
                        new_moveto_parent[key] = get_object(active_objects = self.active_objects, iid = self.original_item_iid)

                set_object(database = self.active_objects, iid = moveto_parent_iid, to_add = new_moveto_parent)

                # Delete original object
                original_parent = get_object(active_objects = self.active_objects, iid = self.original_parent_iid)
                del original_parent[self.original_item_iid.split("\\")[-1]]

                # Delete the old object and re-render the treeview (we can't just move the objects around - the IIDs need to change due to the folder change)
                treeview.delete(self.original_item_iid)
                fill_objects_tree(treeview, self.active_objects, self.object_image, self.folder_image)
                new_iid = moveto_parent_iid + "\\" + self.original_item_iid.split("\\")[-1]
                treeview.move(new_iid, moveto_parent_iid, moveto_index + 1)
                self.modified_and_not_saved = True

            else:
                pass
                #print("NO RELEASE TRIGGERED")

            self.root.config(cursor = "arrow")
            self.moving_object = False

    def move_function(self, event):
        treeview = event.widget
        moveto_index = treeview.index(treeview.identify_row(event.y))   

        try: 
            self.original_item_iid = treeview.selection()[0]

        except IndexError:
            return

        # Visually move the function
        treeview.move(self.original_item_iid, '', moveto_index)

        # Get the new order of the dictionary keys
        iid_list = treeview.get_children()
        key_list = [None] * len(iid_list)

        for i in range(len(iid_list)):
            key_list[i] = iid_list[i].split("\\")[-1]

        # Recreate the dictionary so it's in the right order
        new_dict = {}

        for key in key_list:
            new_dict[key] = self.active_functions[key]

        self.active_functions = new_dict.copy()
        self.modified_and_not_saved = True



    def not_implemented_popup(self):
        open_popup(self.root, "NotImplementedError", "Function not implemented yet")

    def yes_no_popup(self, title_text, body_text, yes_func, no_func = None, default = "Yes"):
        popup = tk.Toplevel(self.root)
        popup.title(title_text)
        popup.grab_set()            # Can't click on anything else whilst the popup window is open

        # Set main body text
        tk.Label(popup, text = body_text).grid(row = 0, column = 0)

        # Button for closing
        yes_button = tk.Button(popup, text = "Yes", command = lambda : yes())
        no_button = tk.Button(popup, text = "No", command = lambda : no())

        yes_button.bind("<Return>", lambda x : yes())
        no_button.bind("<Return>", lambda x : no())

        yes_button.grid(row = 1, column = 0)
        no_button.grid(row = 1, column = 1)

        if default == "Yes":
            yes_button.focus()
        if default == "No":
            no_button.focus()

        popup.attributes('-topmost', 'true')         # Keep the window on top always
        
        def yes():
            yes_func()
            popup.destroy()

        def no():

            if no_func == None:
                pass

            else:
                no_func()

            popup.destroy()



    def add_folder(self, editing = False):

        # Get the selected item and fill the entry with its name
        selected_item_iid = str(self.objects_tree.focus())
        key_list = selected_item_iid.split("\\")
        key_list.pop(0)                                     # Index 0 is always just an empty string ('')

        # Get the ObjectStore (or dict if it's a folder) object
        selected_object = get_object(self.active_objects, selected_item_iid)

        if editing:
            # Get the old name
            old_name = key_list[-1]

            # Get the index in the TreeView
            treeview_index = self.objects_tree.index(selected_item_iid)
            
        # Initial interface set up
        self.new_folder_window = tk.Toplevel(self.root)
        self.new_folder_window.columnconfigure(1, weight = 1)
        self.new_folder_window.title("Create new folder")
        self.new_folder_window.grab_set()                               # Can't click on anything else whilst the add_folder window is open

        # Bind 'Enter' to the save button
        self.new_folder_window.bind("<Return>", lambda event : save())

        self.name_label = tk.Label(self.new_folder_window, text = "Name")
        self.name_var = tk.StringVar(self.new_folder_window)
        self.name_entry = ttk.Entry(self.new_folder_window, textvar = self.name_var)
        self.save_button = ttk.Button(self.new_folder_window, command = lambda : save(), text = "Save")

        self.name_label.grid(column = 0, row = 0)
        self.name_entry.grid(column = 1, row = 0, sticky = "nsew")
        self.save_button.grid(column = 2, row = 0)
        self.name_entry.focus()

        # Fill in the old name if we're editing a folder
        if editing:
            self.name_var.set(old_name)

        # Resize width to a nice size
        self.new_folder_window.update()
        self.new_folder_window.geometry(f"300x{self.new_folder_window.bbox()[3]}")

        def save():

            new_name = self.name_var.get()

            if new_name == "":

                open_popup(self.new_folder_window, "Name error", "Name cannot be blank.")
                return

            else:

                # If the user selected a dictionary, that means they clicked on a folder, so add the new item under it. The exception is if they're editing a folder.
                # Otherwise they clicked on an object, so add the new item in the same folder as that object
                if (editing) or (type(selected_object) is not dict):
                    key_list.pop(-1)

                # Edit the active objects dictionary
                temp_dict = self.active_objects
                for key in key_list:
                    temp_dict = temp_dict[key]

                # Check if this name already exists
                if ((editing and new_name != old_name) or (not editing)) and (new_name in temp_dict.keys()):
                    open_popup(self.new_folder_window, "Name already exists", f"Item already exists in this folder with the name '{new_name}'")
                    return

                if editing:

                    # Update the dictionary
                    temp_dict[new_name] = temp_dict[old_name]

                    # We only need to delete the old dictionary entry, and update the Treeview, if the name has changed
                    if new_name != old_name:

                        # Delete the old entries in the dictionary
                        del temp_dict[old_name]

                        # Delete the item from the TreeView
                        self.objects_tree.delete(selected_item_iid)

                        # Re-render the objects Treeview - we can't just re-insert the folder, as we need to also re-insert all its children
                        fill_objects_tree(self.objects_tree, self.active_objects, object_image = self.object_image, folder_image = self.folder_image)
                    
                        # Highlight the object that was just edited
                        parent_iid = '\\' + '\\'.join(key_list)

                        if parent_iid == '\\':
                            parent_iid = ''    # In case there is no parent, correct the parent iid

                        new_iid = parent_iid + '\\' + new_name

                        self.objects_tree.selection_set(new_iid)

                else:
                    temp_dict[new_name] = {}

                    # Re-render the objects Treeview and close the window
                    fill_objects_tree(self.objects_tree, self.active_objects, object_image = self.object_image, folder_image = self.folder_image)
                
                self.new_folder_window.destroy()
                self.modified_and_not_saved = True

    def delete_object(self):
        # Get the selected item
        selected_item_iid = str(self.objects_tree.focus())

        key_list = selected_item_iid.split("\\")
        key_list.pop(0)                                     # Index 0 is always just an empty string ('')

        def yes_func():
            # Delete the item from the TreeView
            self.objects_tree.delete(selected_item_iid)

            # Delete the item from the active objects dictionary
            temp_dict = self.active_objects

            for key in key_list[0:-1]:
                temp_dict = temp_dict[key]

            del temp_dict[key_list[-1]]
            self.modified_and_not_saved = True

        if tk.messagebox.askyesno("Delete object", f"Delete object '{key_list[-1]}'?"):
            yes_func()


    def execute_function(self):
        # Get the selected item
        selected_item_iid = str(self.functions_tree.focus())
        key_list = selected_item_iid.split("\\")                # Will only ever contain two objects, index 0 being an empty string ('') and index 1 being the active_functions dictionary key 
        key = key_list[1]                                     

        selected_function = self.active_functions[key]          # This will be a FunctionStore object

        print(f"Executing function '{key}' at position {list(self.active_functions).index(key)}...", end = '')
        
        try:
            self.modified_and_not_saved = True
            selected_function.execute()
            print("Completed")
    
        except Exception as e:
            print("FAILED")
            print(repr(e))
            raise e

    def delete_function(self):
        # Get the selected item
        selected_item_iid = str(self.functions_tree.focus())

        key_list = selected_item_iid.split("\\")
        key_list.pop(0)                                     # Index 0 is always just an empty string ('')

        def yes_func():
            # Delete the item from the TreeView
            self.functions_tree.delete(selected_item_iid)

            # Delete the item from the active functions dictionary
            del self.active_functions[key_list[-1]]
            self.modified_and_not_saved = True

        if tk.messagebox.askyesno("Delete function", f"Delete function '{key_list[-1]}'?"):
            yes_func()

    def run_all_functions(self):
        print("Executing all functions")
        failed = False

        for i in range(len(self.active_functions)):
            function_store = list(self.active_functions.values())[i]
            function_obj = function_store.function
            print(f"Executing function type '{function_obj.__name__}' at position {i}... ", end = '')

            try:
                self.modified_and_not_saved = True
                function_store.execute()
                print("Completed")

            except Exception as e:
                print("FAILED")
                print(repr(e))
                failed = True
                raise e

        
        if not failed:
            print("Finished executing all functions")



    def obj_fnc_window(self, obj_or_fnc, index_if_new = None):
        """Create the window used to add new objects or functions, or edit existing ones

        Args:
            obj_or_fnc (str): "object" or "function".
            index_if_new (optional): The index for the object of function (from the master list that the user submits). Defaults to None, which means the user is trying to edit an existing item, not make a new one.
        """

        def retrieve_user_inputs():
                """Iterate through the user inputs in chronological order and update them. This is needed since the UI can change depending on the value of the inputs."""

                for i in range(len(self.input_variables)):
                    keys = list(self.inputs_dict.keys())

                    # StringVar and IntVar are retrieved the same way
                    if isinstance(self.input_variables[i], tk.StringVar) or isinstance(self.input_variables[i], tk.IntVar):
                        self.input_values[keys[i]] = self.input_variables[i].get()
                    
                    # For variable numbers of inputs we must retrieve each input, and we'll add it to a list
                    elif isinstance(self.input_variables[i], list):
                        
                        self.input_values[keys[i]] = []

                        for j in range(len(self.input_variables[i])):
                            self.input_values[keys[i]].append(self.input_variables[i][j].get())
                            
                    # If not yet rendered, fill with None
                    elif self.input_variables[i] is None:
                        self.input_values[keys[i]] = None

                    else:
                        raise ValueError(f"Encountered an unexpected input value type ('{type(self.input_variables[i])}') when trying to run 'retrieve_user_inputs()'")

        def add_to_input_list(datatype_string, frame, variable_list):
            
            def destroy_list(list):
                for object in list:
                    object.destroy()

            if callable(datatype_string):
                raise ValueError("You cannot have functional datatypes within a variable length input.")

            elif datatype_string == "raw":
                variable_list.append(tk.StringVar(frame))

                entry = ttk.Entry(frame, textvar = variable_list[-1])
                entry.grid(column = 0, sticky = "nsew")

                link_button = ttk.Button(frame, text = "Link", command = lambda variable = variable_list[-1]: object_explorer(self.root,
                                                                                                                self.active_objects,
                                                                                                                variable,
                                                                                                                object_image = self.object_image,
                                                                                                                folder_image = self.folder_image,
                                                                                                                object_type = String,
                                                                                                                grab_set = self.main_window))
                link_button.grid(row = frame.grid_size()[1] - 1, column = 1)
                
                destroy_button = ttk.Button(frame, text = "x", width = 2)
                destroy_button.grid(row = frame.grid_size()[1] - 1, column = 2)
                destroy_button.configure(command = lambda entry = entry, link_button = link_button, destroy_button = destroy_button : destroy_list([entry, 
                                                                                                                                                    link_button, 
                                                                                                                                                    destroy_button]))

            elif datatype_string == "object":
                variable_list.append(tk.StringVar(frame))
                entry = ttk.Entry(frame, textvar = variable_list[-1])
                entry.grid(column = 0, sticky = "nsew")

                choose_button = ttk.Button(frame, text = "Choose object", command = lambda variable = variable_list[-1]: object_explorer(self.root,
                                                                                                                        self.active_objects,
                                                                                                                        variable,
                                                                                                                        object_image = self.object_image,
                                                                                                                        folder_image = self.folder_image,
                                                                                                                        grab_set = self.main_window))
                choose_button.grid(row = frame.grid_size()[1] - 1, column = 1)

                destroy_button = ttk.Button(frame, text = "x", width = 2)
                destroy_button.grid(row = frame.grid_size()[1] - 1, column = 2)
                destroy_button.configure(command = lambda entry = entry, choose_button = choose_button : destroy_list([entry, choose_button]))


            elif datatype_string == "file":
                variable_list.append(tk.StringVar(self.new_object_window))
                entry = ttk.Entry(frame, textvar = variable_list[-1])
                entry.grid(column = 0, sticky = "nsew")

                choose_button = ttk.Button(frame, text = "Choose file", command = lambda variable = variable_list[-1]: open_file_to_text_var(variable))
                choose_button.grid(row = frame.grid_size()[1] - 1, column = 1)

                destroy_button = ttk.Button(frame, text = "x", width = 2)
                destroy_button.grid(row = frame.grid_size()[1] - 1, column = 2)
                destroy_button.configure(command = lambda entry = entry, choose_button = choose_button : destroy_list([entry, choose_button]))

                
            elif datatype_string[0:8] == "dropdown":
                dropdown_options = datatype_string.split("_")[1:]
                variable_list.append(tk.StringVar(self.new_object_window))
                combo_box = ttk.Combobox(frame, textvariable = variable_list[-1], state = 'readonly').grid(column = 0, sticky = "nsew")
                combo_box['values'] = dropdown_options
                combo_box.bind("<<ComboboxSelected>>", lambda x : refresh_inputs_ui())      # Update input types when you click on a combobox option

                # Set to first option as default
                combo_box.current(0)

                destroy_button = ttk.Button(frame, text = "x", width = 2)
                destroy_button.grid(row = frame.grid_size()[1] - 1, column = 2, sticky = "nsew")
                destroy_button.configure(command = lambda combo_box = combo_box: destroy_list([combo_box]))

            elif datatype_string == "disabled":
                variable_list.append(tk.StringVar(self.new_object_window))
                box = ttk.Entry(frame, textvar = variable_list[-1]).grid(column = 0, sticky = "nsew")
                box.config(state = "disabled")

                destroy_button = ttk.Button(frame, text = "x", width = 2)
                destroy_button.grid(row = frame.grid_size()[1] - 1, column = 2)
                destroy_button.configure(command = lambda box = box: destroy_list([box]))


            else:
                raise ValueError("Failed to add input label for datatype '{}'".format(datatype_string))

        def add_input_box(datatype, i, force_re_render = False):
            """Add an input box to the GUI and render it.

            Args:
                datatype (str or callable): The original datatype that the user gave. Can be a string or a callable if it's functional.
                i (int): The index of the input in the input dictionary
            """
            retrieve_user_inputs()
            key = list(self.inputs_dict.keys())[i]

            # Non-functional inputs only need to be rendered once
            if not force_re_render and self.inputs_rendered and not callable(datatype):
                return

            # Don't re-render functional inputs if the datatype is the same
            elif callable(datatype) and datatype(self.input_values) == self.current_datatypes[i]:
                return

            # Everything else will be a functional input, which has a new datatype we must change to
            else:
                # Destroy a widget if it needs to be re-rendered
                if self.inputs_rendered == True:
                    if type(self.input_boxes[i]) is list:
                        for j in range(len(self.input_boxes[i])):
                            self.input_boxes[i][j].destroy()
                            
                    else:
                        self.input_boxes[i].destroy()

            # Use a recursive function for the functional inputs
            if callable(datatype):
                actual_datatype = datatype(self.input_values)
                add_input_box(actual_datatype, i, force_re_render = True)
                return

            # This is an input where you can keep adding rows with an "Add ..." button
            elif isinstance(datatype, list):
                self.current_datatypes[i] = datatype
                self.input_variables[i] = []
                self.input_boxes[i] = tk.Frame(self.main_frame)        # We'll add a new entry in this frame every time the user uses the "Add" button
                self.input_boxes[i].columnconfigure(0, weight = 1)     # So it scales to fill the width of the window

                ttk.Button(self.input_boxes[i], 
                            text = f"Add to {key}", 
                            command = lambda frame = self.input_boxes[i], datatype = self.current_datatypes[i][0], variables = self.input_variables[i]:  add_to_input_list(datatype, 
                                                                                                                                                                            frame, 
                                                                                                                                                                            variables)).grid(row = 0, 
                                                                                                                                                                                            column = 0,
                                                                                                                                                                                            columnspan = 3, 
                                                                                                                                                                                            sticky = 'nesw')

            elif type(datatype) is not str:
                raise ValueError("Values from the 'get_inputs' dictionary should be functions or a strings only. Received datatype {}".format(type(datatype)))

            elif datatype == "raw":
                self.current_datatypes[i] = datatype
                self.input_variables[i] = tk.StringVar(self.main_window)
                self.input_boxes[i] = [ttk.Entry(self.main_frame, textvar = self.input_variables[i]),
                                    ttk.Button(self.main_frame, text = "Link", command = lambda variable = self.input_variables[i]: object_explorer(self.root,
                                                                                                                                                        self.active_objects,
                                                                                                                                                        variable,
                                                                                                                                                        object_image = self.object_image,
                                                                                                                                                        folder_image = self.folder_image,
                                                                                                                                                        object_type = String,
                                                                                                                                                        grab_set = self.main_window))]
                
            elif datatype == "object":
                self.current_datatypes[i] = datatype
                self.input_variables[i] = tk.StringVar(self.main_window)
                self.input_boxes[i] = [ttk.Entry(self.main_frame, textvar = self.input_variables[i]), 
                                            ttk.Button(self.main_frame, text = "Choose object", command = lambda variable = self.input_variables[i]: object_explorer(self.root,
                                                                                                                                                                        self.active_objects,
                                                                                                                                                                        variable,
                                                                                                                                                                        object_image = self.object_image,
                                                                                                                                                                        folder_image = self.folder_image,
                                                                                                                                                                        grab_set = self.main_window))]

            elif datatype == "file":
                self.current_datatypes[i] = datatype
                self.input_variables[i] = tk.StringVar(self.main_window)
                self.input_boxes[i] = [ttk.Entry(self.main_frame, textvar = self.input_variables[i]), None]
                self.input_boxes[i][1] = ttk.Button(self.main_frame, text = "Choose file", command = lambda entry = self.input_boxes[i][0]: open_file(entry))
                
            elif datatype[0:8] == "dropdown":
                self.current_datatypes[i] = datatype
                dropdown_options = datatype.split("_")[1:]
                self.input_variables[i] = tk.StringVar(self.main_window)
                self.input_boxes[i] = SortableCombobox(self.main_frame, textvariable = self.input_variables[i], state = 'readonly')
                self.input_boxes[i]['values'] = dropdown_options
                self.input_boxes[i].bind("<<ComboboxSelected>>", lambda x : refresh_inputs_ui())      # Update input types when you click on a combobox option
                self.input_boxes[i].current(0)  # Set to first option as default

            elif datatype == "disabled":
                self.current_datatypes[i] = datatype
                self.input_variables[i] = tk.StringVar(self.main_window)
                self.input_boxes[i] = ttk.Entry(self.main_frame, textvar = self.input_variables[i])
                self.input_boxes[i].config(state = "disabled")

            else:
                raise ValueError("Failed to add input label for key = {}, value = {}".format(key, datatype))

            # Pack the widget and made the entry box scale with the window (sticky = nsew)
            if type(self.input_boxes[i]) is list:
                for j in range(len(self.input_boxes[i])):
                    self.input_boxes[i][j].grid(column = 1 + j, row = i, sticky = "nsew")
                    
            else:
                self.input_boxes[i].grid(column = 1, row = i, sticky = "nsew")

        def add_output_box(datatype, i):
            """Add an output box to the UI.

            Args:
                datatype (str): The datatype that the user gave.
                i (int): The index of the output from the outputs dictionary.
            """

            if datatype == "file":
                self.output_variables[i] = tk.StringVar(self.main_window)
                self.output_boxes[i] = [ttk.Entry(self.main_frame, textvar = self.output_variables[i]), None]
                self.output_boxes[i][1] = ttk.Button(self.main_frame, text = "Choose file", command = lambda entry = self.output_boxes[i][0]: open_file(entry))
                
            else:
                self.output_variables[i] = tk.StringVar(self.main_window)
                self.output_boxes[i] = [ttk.Entry(self.main_frame, textvar = self.output_variables[i]), 
                                            ttk.Button(self.main_frame, text = "Choose object", command = lambda variable = self.output_variables[i]: object_explorer(self.root,
                                                                                                                                                                        self.active_objects,
                                                                                                                                                                        variable,
                                                                                                                                                                        object_image = self.object_image,
                                                                                                                                                                        folder_image = self.folder_image,
                                                                                                                                                                        grab_set = self.main_window))]

            # Pack the widget in a grid
            for j in range(len(self.output_boxes[i])):
                self.output_boxes[i][j].grid(column = 1 + j, row = i + len(self.inputs_dict), pady = (pady, 0), sticky = "nsew")
            
        def refresh_inputs_ui():
            """Re-renders the interface, modifying any intput formats that may be 'functional'."""

            keys = list(self.inputs_dict.keys())
            datatypes = list(self.inputs_dict.values())

            retrieve_user_inputs()  

            for i in range(len(self.inputs_dict)):
                
                # Add the name labels if this is the first time running this function
                if not self.inputs_rendered:
                    self.input_labels[i] = ttk.Label(self.main_frame, text = keys[i])
                    self.input_labels[i].grid(column = 0, row = i, sticky = "n")

                # Add the entries, dropdowns, etc.
                add_input_box(datatypes[i], i)

        def open_file(entry_to_fill):
            """Create a window that you can ue to open a file.

            Args:
                entry_to_fill (tk.Entry): The entry box to fill with the file result.
            """
            filename = tk.filedialog.askopenfilename(initialdir = "/",
                                                    title = "Open file")

            entry_to_fill.delete(0, "end")
            entry_to_fill.insert(0, filename)
            raise_above_all(self.main_window)   # Is this necessary?

        def open_file_to_text_var(text_var):
            filename = tk.filedialog.askopenfilename(initialdir = "/",
                                                    title = "Open file")

            text_var.set(filename)
            raise_above_all(self.new_object_window)

        def save():
            if self.name_var.get() == "":
                open_popup(self.main_window, "Name error", "Name cannot be blank.")

            else:
                # Collect inputs
                retrieve_user_inputs()
              
                # Check if any references to object or file inputs are valid
                for key, value in self.input_values.items():

                    if self.inputs_dict[key] == "raw" and ("\\" in str(value)):

                        try:
                            linked_object = get_object(self.active_objects, value)
                        
                        except KeyError:
                            open_popup(self.main_window, "String link error", f"Link for {key} could not be found (no object exists at {value})")
                            return

                        if type(linked_object) is not ObjectStore or type(linked_object.get_object()) is not String:
                            open_popup(self.main_window, "String link error", "Input for {} is type '{}', when it should be of type String.".format(key, linked_object))
                            return

                    elif self.inputs_dict[key] == "object":
                        
                        if "\\" not in value:
                            open_popup(self.main_window, "Object link error", "Could not find the object for input '{}' located at '{}'.".format(key, value))
                            return

                        try:
                            linked_object = get_object(self.active_objects, value)

                        except KeyError:
                            open_popup(self.main_window, "Object link error", "Could not find the object for input '{}' located at '{}'.".format(key, value))
                            return

                    elif self.inputs_dict[key] == "file":
                        if not os.path.exists(value):
                            open_popup(self.main_window, "File link error", "Could not find a file or folder for input '{}' located at '{}'.".format(key, value))
                            return

                    # Check every item in a list for a variable length input
                    elif isinstance(self.inputs_dict[key], list):
                        if self.inputs_dict[key][0] == "object":
                            for sub_item in value:
                                if "\\" not in sub_item:
                                    open_popup(self.main_window, "Object link error", "Could not find the object for input '{}' located at '{}'.".format(key, sub_item))
                                    return

                                try:
                                    linked_object = get_object(self.active_objects, sub_item)

                                except KeyError:
                                    open_popup(self.main_window, "Object link error", "Could not find the object for input '{}' located at '{}'.".format(key, sub_item))
                                    return

                
                if obj_or_fnc == "function":
                    # Collect outputs
                    for i in range(len(self.outputs_dict)):
                        key = list(self.outputs_dict.keys())[i]
                        self.output_values[key] = self.output_variables[i].get()

                    # If the user's output is supposed to be an object, check that it has "\" at the beginning. If the datatype is "file" then skip this (check that by just checking if it's a string)
                    for key, value in self.output_values.items():
                        if not isinstance(master_data.outputs()[key], str):
                            if self.output_values[key] == "":
                                pass
                            elif self.output_values[key][0] != "\\":
                                tk.messagebox.showinfo("Output error", f"Output directory for '{key}' is not a valid object directory. '{value}' was given, but it must start with '\\'", parent = self.main_window)
                                return


                # Check if the user-chosen name already exists
                new_name = self.name_var.get()

                # Update the dictionary
                if obj_or_fnc == "function":

                    # Check if a function with this name already exists
                    if new_name in database.keys():
                        if not (index_if_new == None and new_name == old_name):
                            open_popup(self.main_window, "Name already exists", "Item already exists in this folder with the name '{}'".format(self.name_var.get()))
                            return

                    combined_in_out_dict = {"\\INPUTS\\" : self.input_values, "\\OUTPUTS\\" : self.output_values}
                    set_item(database = database, iid = new_name, to_add = storage_class(application = self, index = item_index, dictionary = combined_in_out_dict))

                elif obj_or_fnc == "object":
                    if type(selected_item) is not dict:
                        key_list.pop(-1)

                    # Edit the active objects dictionary
                    temp_dict = self.active_objects
                    for key in key_list[1:]:
                        temp_dict = temp_dict[key]

                    # Check if this name already exists
                    if index_if_new == None:
                        if new_name != old_name and new_name in temp_dict.keys():
                            open_popup(self.main_window, "Name already exists", "Item already exists in this folder with the name '{}'".format(self.name_var.get()))
                            return
                    
                    elif new_name in temp_dict.keys():
                            open_popup(self.main_window, "Name already exists", "Item already exists in this folder with the name '{}'".format(self.name_var.get()))
                            return   

                    # Update the dictionary
                    temp_dict[new_name] = storage_class(self, item_index, {"\\INPUTS\\" : self.input_values})


                # We only need to delete the old dictionary entry, and update the Treeview, if the name has changed
                if index_if_new == None:

                    treeview_index = treeview.index(selected_item_iid)

                    if obj_or_fnc == "function":
                        if new_name != old_name:
                            # Delete the old entries in the dictionary
                            del self.active_functions[old_name]

                            # Delete the item from the TreeView
                            self.functions_tree.delete(selected_item_iid)

                            #Re-insert the new function into the Treeview at the same position
                            new_iid = '\\' + new_name
                            self.functions_tree.insert('', treeview_index, new_iid, text = new_name)      # Parent ID, Position, ID, Displayed Text

                            # Highlight the object that was just edited
                            self.functions_tree.selection_set(new_iid)

                    elif obj_or_fnc == "object":
                        # Delete the old entries in the dictionary
                        if new_name != old_name:
                            del temp_dict[old_name]

                            # Delete the item from the TreeView
                            self.objects_tree.delete(selected_item_iid)

                            #Re-insert the new function into the Treeview at the same position
                            parent_iid = '\\'.join(key_list)

                            if parent_iid == '\\':
                                parent_iid = ''    # In case there is no parent, correct the parent iid

                            new_iid = parent_iid + '\\' + new_name

                            print(f"parent_iid = {parent_iid}")

                            self.objects_tree.insert(parent_iid, treeview_index, new_iid, text = new_name, image = self.object_image)      # Parent ID, Position, ID, Displayed Text

                            # Highlight the object that was just edited
                            self.objects_tree.selection_set(new_iid)

                            # If in the future, we want to re-open any renamed folders, we can use these:
                            # https://stackoverflow.com/questions/20531783/retrieving-ttk-treeview-items-open-option-as-boolean
                            # https://stackoverflow.com/questions/59594483/tkinter-treeview-expand-all-child-nodes

                else:
                    # Re-render the  Treeview and close the window
                    fill_tree(treeview, database, object_image = self.object_image, folder_image = self.folder_image) 

                self.main_window.destroy()
                self.modified_and_not_saved = True


        # Pre-collect the required functions and data for either objects or functions
        if obj_or_fnc == "object":
            treeview = self.objects_tree
            database = self.active_objects
            get_item = get_object
            set_item = set_object
            master_list = self.objects
            storage_class = ObjectStore
            fill_tree = fill_objects_tree
        
        elif obj_or_fnc == "function":
            treeview = self.functions_tree
            database = self.active_functions
            get_item = get_function
            set_item = set_function
            master_list = self.functions
            storage_class = FunctionStore
            fill_tree = fill_functions_tree

        else:
            raise ValueError(f"'type' must be 'object' or 'function', not '{type}'")

        selected_item_iid = str(treeview.focus())
        key_list = selected_item_iid.split("\\")
        if obj_or_fnc == "function" and selected_item_iid == "":
            pass
        else:
            selected_item = get_item(database, selected_item_iid)

        if index_if_new == None:
            # Editing an existing item

            if type(selected_item) is dict:         # This indicates a folder is being edited
                self.add_folder(editing = True)
                return

            item_index = selected_item.index
            master_data = master_list[item_index]
            old_name = key_list[-1]

        else:
            # Creating a new item
            item_index = index_if_new
            master_data = master_list[item_index]

        # Initialise main window
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("Create new {}".format(str(master_data.__name__)))
        self.main_window.bind("<1>", lambda event : refresh_inputs_ui())   
        self.main_window.bind("<Return>", lambda event : refresh_inputs_ui())     
        self.main_window.grab_set()              
        self.main_window.grid_rowconfigure(0, weight = 1)           # So entries scale to fill the width of the window
        self.main_window.grid_columnconfigure(0, weight = 1)                    

        self.main_frame = tk.Frame(self.main_window)                # Frame that everything is in (is this necessary?)
        self.main_frame.grid(sticky = "nsew")
        self.main_frame.columnconfigure(1, weight = 1)              # So entries scale to fill the width of the window

        # Initialise lists
        self.inputs_dict = master_data.inputs()

        self.input_labels = [None] * len(self.inputs_dict)               # Labels showing the input name
        self.current_datatypes = [None] * len(self.inputs_dict)          # Used to check when input datatypes change and need to be re-rendered
        self.input_boxes = [None] * len(self.inputs_dict)                # Boxes containing the widgets the users use to enter the inputs
        self.input_variables = [None] * len(self.inputs_dict)            # List containing the variables linked to the input boxes
        self.input_values = {}                                          # Dict of the current input values (used to evaluate functional inputs)

        if obj_or_fnc == "function":
            self.outputs_dict = master_data.outputs()

            self.output_labels = [None] * len(self.outputs_dict) 
            self.output_boxes = [None] * len(self.outputs_dict)
            self.output_variables = [None] * len(self.outputs_dict)
            self.output_values = {}                                          

        # Add button for adding a name and saving
        self.name_label = tk.Label(self.main_frame, text = "Name")
        self.name_var = tk.StringVar(self.main_window)
        self.name_entry = ttk.Entry(self.main_frame, textvar = self.name_var)
        self.save_button = ttk.Button(self.main_frame, command = lambda : save(), text = "Save")

        self.name_entry.bind("<Return>", lambda x : save())
        self.save_button.bind("<Return>", lambda x : save())

        # Generate UI
        self.inputs_rendered = False

        refresh_inputs_ui()
        
        # Render the name entry at the bottom
        self.name_label.grid(column = 0, row = len(self.inputs_dict) + 1, pady = (15, 0))
        self.name_entry.grid(column = 1, row = len(self.inputs_dict) + 1, pady = (15, 0), sticky = "nsew")
        self.save_button.grid(column = 2, row = len(self.inputs_dict) + 1, pady = (15, 0))


        # Only generate outputs once
        if obj_or_fnc == "function":
            for i in range(len(self.outputs_dict)):
                if i == 0:
                    pady = 15
                else:
                    pady = 0

                self.output_labels[i] = ttk.Label(self.main_frame, text = list(self.outputs_dict.keys())[i])
                self.output_labels[i].grid(column = 0, row = i + len(self.inputs_dict), pady = (pady, 0))
                add_output_box(list(self.outputs_dict.values())[i], i)


        # Tooltips
        create_tool_tip(widget = self.name_label, text = "Name to give the object when you save it")

        try:
            input_tips = master_data.input_tips()

            try:
                for label in self.input_labels:
                    create_tool_tip(widget = label, text = input_tips[label["text"]])
                    
            except KeyError:
                pass

        except AttributeError:
            pass
        
        if obj_or_fnc == "function":
            try:
                output_tips = master_data.output_tips()
                for label in self.output_labels:
                    create_tool_tip(widget = label, text = output_tips[label["text"]])

            except AttributeError:
                pass
        
        # If we're editing an object, then fill the boxes with the current values
        def fill_inputs():
            # Fill the name entry with what it currently is
            self.name_var.set(old_name)   

            # Get the Treeview index of the item that was selected
            treeview_index = treeview.index(selected_item_iid)   

            # Fill the input boxes
            old_values = list(selected_item.dictionary["\\INPUTS\\"].values())
            keys = list(self.inputs_dict.keys())

            for j in range(len(self.input_variables)):
                # Special case needed for list inputs
                if isinstance(self.input_variables[j], list):
                    for k in range(len(old_values[j])):
                        
                        add_to_input_list(datatype_string = self.inputs_dict[keys[j]][0], frame = self.input_boxes[j], variable_list = self.input_variables[j])
                        self.input_variables[j][k].set(old_values[j][k])

                else: 
                    self.input_variables[j].set(old_values[j])

            # Fill the output boxes
            if obj_or_fnc == "function":
                old_values = list(selected_item.dictionary["\\OUTPUTS\\"].values())
                for j in range(len(self.output_variables)):
                    self.output_variables[j].set(old_values[j])

        
        if index_if_new == None:
            num_functional = 0

            self.inputs_rendered = True
            fill_inputs()
            refresh_inputs_ui() # Re-render any functional inputs - this will clear the entry in it, so we need to fill it again

            for datatype in self.inputs_dict.values():
                if callable(datatype):
                    num_functional += 1

            for i in range(num_functional):
                fill_inputs()
                refresh_inputs_ui()


        # Highlight the first box
        if len(self.input_boxes) > 0:
            if type(self.input_boxes[0]) is list:
                self.input_boxes[0][0].focus()
            else:
                self.input_boxes[0].focus()


        self.inputs_rendered = True

        # Resize width to a nice size
        self.main_window.update()

        has_list = False
        for datatype in self.inputs_dict.values():
            if isinstance(datatype, list):
                has_list = True
        if has_list:
            self.main_window.geometry(f"400x{self.main_window.bbox()[3] + 100}") # Add a bit more room if there's a list that will move things down
        else:
            self.main_window.geometry(f"400x{self.main_window.bbox()[3]}")


    def get_axes(self, title = "Plot", three_d = False):
        figure = Figure()

        # Create a Toplevel to put the plot in
        plot_window = tk.Toplevel(self.root)
        plot_window.title(title)

        plot_window.wm_transient(self.root)         # Keep the window on top of the main one, but not other applications running on our computer

        # Create FigureCanvasTkAgg object
        figure_canvas = FigureCanvasTkAgg(figure, plot_window)

        # Create the toolbar
        NavigationToolbar2Tk(figure_canvas, plot_window)

        # Create axes - this will be returned to the user, and they can use axes.plot to add something to the plot
        if three_d:
            axes = figure.add_subplot(projection='3d')
        else:
            axes = figure.add_subplot()

        figure_canvas.get_tk_widget().pack(side = "top", fill = "both", expand = 1)

        return axes

