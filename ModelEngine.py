# import basic python modules
import json, importlib

# import the perfomance counter module to measure the model performance
from time import perf_counter

# import the model interface module
from helpers.interface import Interface

class ModelEngine:

    # when a model class is instantiated the model loads de normal neonate json definition by default.
    def __init__(self, filename = 'normal_neonate.json'):
        # define a dictionary with all the needed model classes
        self.component_objects = {}
    
        # define a dictionary with all the components
        self.components = {}

        # define a variable holding the current model clock
        self.model_clock = 0

        # load the model definition file
        self.model_definition = self.load_csv_definition_file(filename)

        # initialize all model components with the parameters from the JSON file
        self.initialize(self.model_definition)

        # define some model performance properties
        self.step_duration = 0
        self.run_duration = 0

    def load_csv_definition_file(self, filename): 
        # open the JSON file
        json_file = open(filename)
    
        # convert the JSON file to a python dictionary
        properties = json.load(json_file)
        
        # return the dictionary
        return properties
  

    def initialize(self, model_definition):
        # set error flag
        error_counter = 0
        
        # get the model stepsize from the model definition
        self.modeling_stepsize = model_definition['modeling_stepsize']
            
        # get the model name from the model definition
        self.name= model_definition['name']
            
        # get the model description from the model definition
        self.description = model_definition['description']
            
        # get the set weight from the model definition
        self.weight = model_definition['weight']
    
        # analyze the model_definition components
        for key in model_definition['components']:
            # get a reference to the component
            _component = model_definition['components'][key]
            
            # get the model type
            _model_type = _component['model_type']
            
            # try to find the desired model class from the core_models or custom_models folder
            try:
                # try to import the module holding the model class from the core_models folder
                _model_class = importlib.import_module('core_models.' + _model_type)
                
                # get the model class from the module
                self.component_objects[_model_type] = getattr(_model_class, _model_type)
                
                # instantiate the model class with the properties stored in the model_definition file and a reference to the other 
                # components and add it to the components dictionary
                self.components[_component['name']] = self.component_objects[_component['model_type']](self, **_component)
            except:
                # can't find the module holding the model class in the core_models folder
                try:
                    # try to import the module holding the model class from the custom_models folder
                    _model_class = importlib.import_module('custom_models.' + _model_type)
                    
                    # get the model class from the module
                    self.component_objects[_model_type] = getattr(_model_class, _model_type)
                    
                    # instantiate the model class with the properties stored in the model_definition file and a reference to the other 
                    # components and add it to the components dictionary
                    self.components[_component['name']] = self.component_objects[_component['model_type']](self, **_component)
                except:
                    # a module holding the desired model class is not found in the core_models or custom_models folder
                    print(f"{_model_type} model not found in the core_models nor in the custom_models folder.")
                    error_counter += 1
            
        if (error_counter == 0):
            print(f"{self.name} model loaded and initialized correctly.")
        else:
            print(f"{self.name} model failed to load correctly producing {error_counter} errors.")
   
        # initialize the model interface
        self.io = Interface(self)


    # calculate a number of seconds
    def calculate(self, time_to_calculate):
        # calculate the number of steps needed (= time in seconds / modeling stepsize in seconds)
        no_steps = int(time_to_calculate / self.modeling_stepsize)
    
        # start the performance counter
        perf_start = perf_counter()

        # execute the model steps
        for _ in range(no_steps):
            for comp in self.components:
                self.components[comp].model_step()


            # call the user interface
            self.io.model_step(self.model_clock)

            # increase the model clock
            self.model_clock += self.modeling_stepsize


        # stop the performance counter
        perf_stop = perf_counter()

        # store the performance metrics
        self.run_duration = perf_stop - perf_start
        self.step_duration = (self.run_duration / no_steps) * 1000