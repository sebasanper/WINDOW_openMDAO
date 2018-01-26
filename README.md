WINDOW_openMDAO

author: Sebastian Sanchez Perez-Moreno
affiliation: Wind Energy Section, Faculty of Aerospace Engineering, TU Delft, the Netherlands
email: s.sanchezperezmoreno@tudelft.nl

WINDOW is an MDAO workflow to design offshore wind farms. It is written in NASA's openMDAO framework.
The following publication by the same author shows the Extended Design Structure Matrix of WINDOW_openMDAO.

Please cite:
Sebastian Sanchez Perez Moreno and Michiel B. Zaaijer. "How to select MDAO workflows", 2018 AIAA/ASCE/AHS/ASC Structures, Structural Dynamics, and Materials Conference, AIAA SciTech Forum, (AIAA 2018-0654) 
https://doi.org/10.2514/6.2018-0654 

---------------------------------------------------

In order to run from a working directory, you need to implement the WorkingGroup class (in workflow_*.py files) and define an OpenMDAO Problem class. All input must be put in a folder called "Input". See and run an example from the "example" folder provided. Run IEA_borssele_irregular.py.