WINDOW_openMDAO

author: Sebastian Sanchez Perez-Moreno
affiliation: Wind Energy Section, Faculty of Aerospace Engineering, TU Delft, the Netherlands
email: s.sanchezperezmoreno@tudelft.nl

WINDOW is an MDAO workflow meant to support the design of offshore wind farms. WINDOW can accommodate different models for the same disciplinary modules, and some models are included in the tool.
It is written in NASA's OpenMDAO framework.
The following publications by the same author shows the Extended Design Structure Matrix of WINDOW.

Please cite:
Sebastian Sanchez Perez Moreno and Michiel B. Zaaijer. "How to select MDAO workflows", 2018 AIAA/ASCE/AHS/ASC Structures, Structural Dynamics, and Materials Conference, AIAA SciTech Forum, (AIAA 2018-0654) 
https://doi.org/10.2514/6.2018-0654 


---------------------------------------------------

To install, go to the directory where you have cloned the module and execute

    python2 setup.py install --user

Then its packages will be available under `from WINDOW_openMDAO import <...>`.

To reinstall after changes to your local copy:

    python2 setup.py install --user --force

[Python 3 is not yet supported.]

---------------------------------------------------

First make sure you have OpenMDAO installed.

    pip install openmdao


In order to run WINDOW from a working directory, you need to implement the WorkingGroup class (in the multifidelity_fast_workflow.py file) and define an OpenMDAO Problem class. All input must be put in a folder called "Input". An Options class (in WINDOW_openMDAO.src.api) must be instantiated and its attributes filled with the desired inputs that instantiate the MDAO workflow, such as models, numer of windrose sampling points and site and turbine input files. See and run an example from the "example" folder provided. Run IEA_borssele_irregular.py.
