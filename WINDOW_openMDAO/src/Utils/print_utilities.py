def beautify_dict(dict):  
    import numpy as np
    DEC=4
    
    for key, val in dict.iteritems():
        val = np.array(val)
        if np.size(val) > 1:
                print key + ' = ' + str(repr(np.around(np.array(val),DEC).tolist()))
        else:
                print key + ' = ' + str(round(val,DEC))