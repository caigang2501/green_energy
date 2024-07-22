import random,math,requests

from example import constent 
import copy

up = constent.DEVICE_LIMIT
FEATURE_NAME = ('风电','光伏','热电联产','燃气锅炉','电锅炉','地源热泵产热','空气源热泵产热','地源热泵制冷','空气源热泵制冷','电制冷机','吸收式制冷机','买天然气','充放电')
variables_range = [(0,up[0]),(0,up[1]),(0,up[2]),(0,up[3]),(0,up[4]),(0,up[5]),(0,up[6]),(0,up[5]),(0,up[6]),(0,up[7]),(0,up[8]),(0,100000),(0,1)]

# print(len(FEATURE_NAME),len(variables_range))
def get_part(sc,k,change=True):
    pda = 2 #总part比上总容量
    choc = sorted(random.choices(list(range(100)),k=k))
    choc.insert(0,0),choc.append(100)
    part = [(choc[i+1]-choc[i])*0.01 for i in range(k+1)]
    if change:
        part = [p/sc[idx]/pda+random.normalvariate(0,0.05)/sc[idx] for idx,p in enumerate(part)]
    else:
        part = [p/sc[idx]/pda for idx,p in enumerate(part)]
    part = [0 if p<0 else round(p,2) for p in part]
    return part
a = {1:[2]}
b = copy.deepcopy(a)
b[1][0] = 3


# by_result = requests.post('http://10.30.107.7:8089/json',json={"run":{}})
# a = by_result.json()
# print('by_result: ',by_result.status_code,a)
# print(len(a['workday']),len(a['weekend']),len(a['holiday']))