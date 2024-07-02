"""
Every object needs a "get_inputs" method. This third is used to generate the user's interface when they create a new object. 
The object's __init__ must take only one input called 'dictionary'. This will be a dictionary of the user's inputs, in the format listed below.

Options for 'inputs':
raw - just a box that the user can type into. Will be provided as a string. Can be linked to scigui.String objects.
object - lets the user pick an object they created. This actual object will be submitted to the function.
file - user can use the file explorer, and the program will return the directory to the function as a string.
dropdown_option1_option2_etc... - dropdown menu, with available options seperated by _. Will be provided as a string.
disabled - Input is greyed out for the user. A blank string will be provided (i.e. '').
[xxx] - If you put one of the above options in square brackets, it lets the user dynamic add more than one entry for this object (using an 'Add more ...' button). This input will be provided as a list.

You can also submit a function, which should take one input (which will be a dictionary of the users current object inputs), and should return a string with 'raw', 'file' or 'dropdown...' 
according to how the input type should vary according to what the object inputs are. These is useful if you want your inputs to vary according to e.g. a dropdown option. Make sure the function
always returns 'disabled' as an 'else' result. Note functional inputs cannot be in square brackets.

Note that the inputs are rendered in the order they appear in the get_inputs() dictionary. Hence, if a 'function' should only rely on inputs
that come before it.
"""

class Debug:
    def __init__(self, dictionary):
        self.raw = dictionary["rawvalue"]
        self.object = dictionary["objectvalue"] 
        self.file = dictionary["filevalue"]
        self.dropdown = dictionary["dropdownvalue"]
        self.disabled = dictionary["disabledvalue"]
        self.functional = dictionary["functional"]
        self.list = dictionary["list"]

    @staticmethod
    def functional(dictionary):
        if dictionary["dropdownvalue"] == "raw":
            return "raw"
        elif dictionary["dropdownvalue"] == "object":
            return "object"
        elif dictionary["dropdownvalue"] == "file":
            return "file"
        elif dictionary["dropdownvalue"] == "dropdown":
            return "dropdown_option1_option2_option3_option4"
        else:
            return "disabled"

    @staticmethod
    def inputs():
        return {"rawvalue" : "raw", 
                "objectvalue" : "object", 
                "filevalue" : "file", 
                "dropdownvalue" : "dropdown_raw_object_file_dropdown_disabled", 
                "disabledvalue" : "disabled",
                "functional" : Debug.functional,
                "list" : ["raw"]} 

    @staticmethod
    def input_tips():
        return {"rawvalue" : "This is a raw value", 
                "objectvalue" : "This is an object you havet to select", 
                "filevalue" : "This is a file you must give the directory to", 
                "dropdownvalue" : "This is a choice of a few dropdowns", 
                "disabledvalue" : "This input is disabled",
                "functional" : "This is an input that changes type, depending on the values of the above inputs",
                "list" : "More than one input can be added here"} 