import numpy as np
import random

import tensorflow as tf
from pygenn import genn_model, genn_wrapper

class ReLUANN():
    def __init__(self,neuron_resting_voltage=-60.0,neuron_threshold_voltage=-55.0,
        membrane_capacitance=1.0, model_timestep=1.0,):
        self.Vres = neuron_resting_voltage
        self.Vthr = neuron_threshold_voltage
        self.Cm = membrane_capacitance
        self.timestep = model_timestep

    def convert(self, tf_model):
        # create custom classes
        if_model = genn_model.create_custom_neuron_class(
            "if_model",
            param_names=["Vres","Vthr","Cm"],
            var_name_types=[("Vmem","scalar"),("SpikeNumber","unsigned int")],
            sim_code="""
            $(Vmem) += $(Isyn)*(DT / $(Cm));
            //printf("Vmem: %f, Isyn: %f, SpikeNumber: %d", $(Vmem),$(Isyn),$(SpikeNumber));
            """,
            reset_code="""
            $(Vmem) = $(Vres); 
            $(SpikeNumber) += 1;
            """,
            threshold_condition_code="$(Vmem) >= $(Vthr)"
        )

        cs_model = genn_model.create_custom_current_source_class(
            "cs_model",
            var_name_types=[("magnitude","scalar")],
            injection_code="""
            $(injectCurrent, $(magnitude));
            """
        )

        # Fetch tf_model details
        n_layers = len(tf_model.layers)
        tf_weights = tf_model.get_weights()

        # Params and init
        if_params = {
            "Vres":self.Vres,
            "Vthr":self.Vthr,
            "Cm":self.Cm
        }
        if_init = {
            "Vmem":genn_model.init_var("Uniform", {"min": self.Vres, "max": self.Vthr}),
            "SpikeNumber":0
        }
        
        cs_init = {"magnitude":10.0}

        # Define model and populations
        self.g_model = genn_model.GeNNModel("float","g_model")
        self.neuron_pops = {}
        self.syn_pops = {}

        for i in range(1,n_layers): # 1,2 - synapses
            if i == 1:
                # Presynaptic neuron
                self.neuron_pops["if"+str(i-1)] = self.g_model.add_neuron_population(
                    "if"+str(i-1),tf_weights[i-1].shape[0],if_model,if_params,if_init
                )

            # Postsynaptic neuron
            self.neuron_pops["if"+str(i)] = self.g_model.add_neuron_population(
                "if"+str(i),tf_weights[i-1].shape[1],if_model,if_params,if_init
            )

            # Synapse
            self.syn_pops["syn"+str(i-1)+str(i)] = self.g_model.add_synapse_population(
                "syn"+str(i-1)+str(i),"DENSE_INDIVIDUALG",genn_wrapper.NO_DELAY,
                self.neuron_pops["if"+str(i-1)], self.neuron_pops["if"+str(i)],
                "StaticPulse",{},{'g':tf_weights[i-1].reshape(-1)},{},{},
                "DeltaCurr",{},{}
            )
        
        self.current_source = self.g_model.add_current_source("cs",cs_model,"if0",{},cs_init)

        self.g_model.dT = self.timestep
        self.g_model.build()
        self.g_model.load()

        return self.g_model

    def evaluate(self, X, y=None, single_example_time=350.):
        n_examples = len(X)
        X = X.reshape(n_examples,-1)
        y = y.reshape(n_examples)

        runtime = n_examples * single_example_time
        i = -1
        n_correct = 0

        while self.g_model.t < runtime:
            if self.g_model.t >= single_example_time*(i+1):
                # After example i -1,0,1,2,..
                self.g_model.pull_var_from_device("if2",'SpikeNumber')
                SpikeNumber_view = self.neuron_pops["if2"].vars["SpikeNumber"].view
                n_correct += (np.argmax(SpikeNumber_view)==y[i])
                i += 1
                # Before example i 0,1,2,3,..
                for j in range(len(self.neuron_pops)):
                    self.neuron_pops["if"+str(j)].vars["SpikeNumber"].view[:] = 0
                    neuron_view = self.neuron_pops["if"+str(j)].vars["Vmem"].view[:] = random.uniform(-60.,-55.)
                    self.g_model.push_state_to_device("if"+str(j))
                
                magnitude_view = self.current_source.vars['magnitude'].view[:] = X[i] / 100.
                self.g_model.push_var_to_device("cs",'magnitude')

            self.g_model.step_time()

        accuracy = (n_correct / n_examples) * 100.
        
        return accuracy