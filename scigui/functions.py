"""
Each function 'object' needs:

inputs() - This is a list of what inputs are needed, and the datatypes (same as for objects) - raw, object, file, dropdown or disabled. Can also be a 'functional' input.
outputs() - This is a list of outputs and the object type that is output. Otherwise you can also just use the string 'file' to imply you want a directory to be given.
execute(dictionary) - this will receive a dictionary containing keys corresponding to 'inputs', and should return a dictionary with keys corresponding to each 'output' (except a file output, 
                      which isn't needed). Each value in the dictionary should be a subdictionary, that can submitted to the corresponding object to create it.

"""

import scigui
import matplotlib.pyplot as plt

class AddNumbers:
    def __init__(self):
        pass
    
    @staticmethod
    def execute(inputs_dictionary, outputs_dictionary):

        result = float(inputs_dictionary["Value 1"]) + float(inputs_dictionary["Value 2"])    # dictionary["Value 1"] and dictionary["Value 2"] will be main.Raw objects (which are equivalent to strings)
        
        inputs_dictionary["\\APPLICATION\\"].popup(title_text = "This is a pop up from AddNumbers", body_text = "Numbers successfully added!")

        return {"Result" : {"Value" : result} }

    @staticmethod
    def outputs():
        return {"Result" : scigui.String}

    @staticmethod
    def inputs():
        return {"Value 1" : "raw",
                "Value 2" : "raw"}

    @staticmethod
    def input_tips():
        return {"Value 1" : "This is one value to add.",
                "Value 2" : "This is another value to add."}

    @staticmethod
    def output_tips():
        return {"Result" : "This is the sum of Value 1 and Value 2."}


class Plot:
    def __init__(self):
        pass
    
    @staticmethod
    def execute(inputs_dictionary, outputs_dictionary):
        xs = [0, 1, 2, 3]
        ys = [0, 1, 1, 0]
        axes = inputs_dictionary["\\APPLICATION\\"].get_axes(title = "First plot!")
        axes.plot(xs, ys)

        ys2 = [0, 1, 1, 3]
        axes2 = inputs_dictionary["\\APPLICATION\\"].get_axes(title = "Second plot!")
        axes2.plot(xs, ys2)

        zs = [0, 2, 5, 3]
        axes3d = inputs_dictionary["\\APPLICATION\\"].get_axes(title = "This one is in 3D!", three_d = True)
        axes3d.plot3D(xs, ys, zs)

    @staticmethod
    def outputs():
        return {}

    @staticmethod
    def inputs():
        return {}

    