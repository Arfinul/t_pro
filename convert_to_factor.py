txt_file = open("result.txt", "r").read()
li = txt_file.split("\n")
frame_count = li[0].split(": ")[1]
_1lb = int(li[1].split(": ")[1])
_2lb = int(li[2].split(": ")[1])
_3lb = int(li[3].split(": ")[1]) 
_1bj = int(li[4].split(": ")[1])
_2bj = int(li[5].split(": ")[1])
_cluster = int(li[6].split(": ")[1])
_coarse = int(li[7].split(": ")[1])
time_taken = li[9].split(": ")[1]
# _perc = round(float(li[8].split(": ")[1]), 2)
# _perc = _perc if math.isnan(float(_perc)) == False else 0

totalCount = int(_1lb + _2lb + _3lb + _1bj + _2bj + _coarse)

_1lb = int(round(_1lb * 1.1346, 0))
_2lb = int(round(_2lb * 1.2006, 0))
_1bj = int(round(_1bj * 1.3288, 0))
_3lb = int(round(_3lb * 1.4213, 0))
_2bj = int(round(_2bj * 0.85, 0))

_coarse = int(round(_coarse - totalCount * 0.012, 0))
_coarse = _coarse if _coarse > 0 else 0

totalCount = _1lb + _2lb + _3lb + _1bj + _2bj + _coarse
try:
    _perc = round(((_1lb + _2lb + (_3lb/2) + _1bj) / totalCount)*100, 2)
except:
    _perc = 0

with open("factor.txt", "w") as factor:
    factor.write("Frame: "+ frame_count + "\n")
    factor.write("1LB: " + str(_1lb) + "\n")
    factor.write("2LB: " + str(_2lb) + "\n")
    factor.write("3LB: " + str(_3lb) + "\n")
    factor.write("1Bj: " + str(_1bj) + "\n")
    factor.write("2Bj: " + str(_2bj) + "\n")
    factor.write("Coarse: " + str(_cluster) + "\n")
    factor.write("Cluster: " + str(_coarse) + "\n")
    factor.write("Total: " + str(totalCount) + "\n")
    factor.write("FLC % " + str(_perc) + "\n")
    factor.write("Time: " + time_taken + "\n")
