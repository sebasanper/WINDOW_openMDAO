from distutils.core import setup

setup(
    name='WINDOW_openMDAO',
    version='',
    description="WINDOW is an MDAO workflow to design offshore wind farms",
    long_description="""
    WINDOW is an MDAO workflow to design offshore wind farms. It is written in
    NASA's openMDAO framework. The following publication shows the Extended
    Design Structure Matrix of WINDOW_openMDAO:

    Sebastian Sanchez Perez Moreno and Michiel B. Zaaijer. “How to select MDAO workflows”,
    2018 AIAA/ASCE/AHS/ASC Structures, Structural Dynamics, and Materials Conference,
    AIAA SciTech Forum, (AIAA 2018-0654) https://doi.org/10.2514/6.2018-0654
    """,
    author="Sebastian Sanchez Perez-Moreno",
    author_email="s.sanchezperezmoreno@tudelft.nl",
    url='https://github.com/sebasanper/WINDOW_openMDAO',
    packages=[
        'WINDOW_openMDAO',
        'WINDOW_openMDAO.src',
        'WINDOW_openMDAO.Costs',
        'WINDOW_openMDAO.ElectricalCollection',
        'WINDOW_openMDAO.Finance',
        'WINDOW_openMDAO.OandM',
        'WINDOW_openMDAO.SupportStructure',
        'WINDOW_openMDAO.Turbine',
        'WINDOW_openMDAO.WakeModel',
        'WINDOW_openMDAO.WaterDepth',
    ]
)
