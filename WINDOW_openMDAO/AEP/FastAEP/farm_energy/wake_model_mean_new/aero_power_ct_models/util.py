def interpolate(minx, miny, maxx, maxy, valx):
    return miny + (maxy - miny) * ((valx - minx) / (maxx - minx))


#-----------parse FAST output file and generate statistics with GNUplot
# with open("FAST_power_ct.out", "r") as data:
#     v = 3.0
#     name = "FAST_power_" + str(v) + ".dat"
#     out = open(name, "w")
#     for line in data:
#         col = line.split()
#         if float(col[1]) == v:
#             out.write("{0:f} {1:f}\n".format(float(col[6]), float(col[5])))
#         else:
#             out.close()
#             v = float(col[1])
#             name = "FAST_power_" + str(v) + ".dat"
#             out = open(name, "w")
#             out.write("{0:f} {1:f}\n".format(float(col[6]), float(col[5])))
#

# with open("stats_script.gp", "w") as script:
#     for v in range(6, 52):
#         script.write("unset print\n")
#         script.write("stats 'FAST_power_{0:1.1f}.dat' u 2\n".format(float(v / 2.0)))
#         script.write("set print 'FASTstatistics_ct.dat' append\n")
#         script.write("print {0:1.1f}, STATS_mean, STATS_stddev\n".format(float(v / 2.0)))
