import re

class Singleton:
    def __init__(self):
        self.value = 0
        self.load = None
st = Singleton()

objectives = []


a = ''
result = re.sub(r'\s+', ',', a)
result = result.split(',')
result = result[6:]+result[:6]
result = ','.join(result)
print(result)


SP_INDIVIDUAL = 1

# 排放系数
ELIC_CO2 = 88.43
CH4_CO2 = 221

# CH4_PRICE = {0:2.5,300:3,600:3.75}
CH4_PRICE = 3.2     # 天然气价格
CH4_POWER = 9.88    # 热值 (kw/m**3)
RATED_CAPACITY = 50000

# 税率
LAMBDA_INT = 0.25 # 所得税
LAMBDA_VAT = 0.13 # 增值税
LAMBDA_UMT = 0.05 # 城市建设维护税
LAMBDA_UMT = 0.05 # 教育费附加费

YEARS = 20
DISCOUNT_RATE = 0.06
LOAN_PERSONT = 0.8
LOAN_RATE = 0.049
REPAYMENT_YEARS = 15

# SPECIAL_DAYS = {'summer':1,'excessive':1,'winter':1}
SPECIAL_9DAYS = {'summer_workday':63,'summer_workend':25,'summer_holiday':4,
                'excessive_workday':64,'excessive_workend':25,'excessive_holiday':4,
                'winter_workday':123,'winter_workend':51,'winter_holiday':6}

EMPTY_SEASON = {'summer_workday':[],'summer_workend':[],'summer_holiday':[],
        'excessive_workday':[],'excessive_workend':[],'excessive_holiday':[],
        'winter_workday':[],'winter_workend':[],'winter_holiday':[]}

FEATURE_RUN_COLUME = ('典型日种类','时间','电负荷','热负荷','冷负荷','风力','光伏','热电联产','燃气锅炉','电锅炉','地制热','空气制热','地制冷','空气制冷','电制冷机','吸收制冷','储电设备','储热设备','储冷设备','储气设备','买燃气','买卖电')
FEATURE_COLUME = ('风电','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气热泵','电制冷机','吸收式制冷机','地源热泵制冷比例','空气源热泵制冷比例','充放然气','充放电')
FEATURE_PLAN_COLUME = ('风力','光伏','热电联产','燃气锅炉','电锅炉','地源热泵','空气热泵','电制冷机','吸收制冷','储电设备','储热设备','储冷设备','储气设备','最大充电','最大充热','最大充冷','最大充气','最大放电','最大放热','最大放冷','最大放气')
ENGLISH_DICT = {'风力':'windPower','光伏':'photovoltaic','热电联产':'coGenerationSystems','燃气锅炉':'gasBoiler','电锅炉':'electricBoiler','地源热泵':'groundSourceHeatPump','空气热泵':'airSourceHeatPump','电制冷机':'electricRefrigerationMachine','吸收制冷':'absorptionRefrigerationMachine','储电设备':'electricityStorageEquipment','储热设备':'thermalStorageEquipment','储冷设备':'coldStorageEquipment','储气设备':'airReservoir',
                '典型日种类':'specialDay','时间':'time','电负荷':'elicLoad','热负荷':'heatLoad','冷负荷':'coldLoad','地制热':'groundSourceHeatPump_heat','地制冷':'groundSourceHeatPump_cold','空气制热':'airSourceHeatPump_heat','空气制冷':'airSourceHeatPump_cold','买燃气':'buyGas','买卖电':'buySellElic','最大充电':'maxChargeElic','最大充热':'maxChargeHeat','最大充冷':'maxChargeCold','最大充气':'maxChargeGas','最大放电':'maxDishargeElic','最大放热':'maxDishargeHeat','最大放冷':'maxDishargeCold','最大放气':'maxDishargeGas'}


# 电价 time: 7->24->6
ELEC_BUY_PRICE = (0.379028,0.685068,0.685068,0.685068,0.685068,0.685068,0.685068,0.685068,0.685068,0.991108,0.991108,0.991108,0.991108,1.139756,1.139756,0.685068,0.685068,0.379028,0.379028,0.379028,0.379028,0.379028,0.379028,0.379028)
# ELEC_BUY_PRICE = [0 for i in range(24)]
ELEC_SELL_PRICE = (0.379028,0.685068,0.685068,0.685068,0.685068,0.685068,0.685068,0.685068,0.685068,0.991108,0.991108,0.991108,0.991108,1.139756,1.139756,0.685068,0.685068,0.379028,0.379028,0.379028,0.379028,0.379028,0.379028,0.379028)
LEFT_ELEC_SELL_PRICE = (0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900,0.282900)


# 设备参数
# '风力','光伏','热电','燃气炉','电锅炉','地源','空气','电制冷','吸收制冷','储电','储热','储冷','储气'
DEVICE_LIMIT = [2000,460,8000,4000,4000,800,2000,1000,4000,10000,10000,10000,2000]
CONV_RATE = (0,0,(0.45, 0.38), 1, 0.97, (5, 4.4),(1.8, 2), 4, 1)
CONSTRA_COST = (6.00,4.00,7.00,0.75,1.20,3.00,5.00,0.97,1.20,2.00,0.80,0.09,0.06)
MAINTAIN_COST = (102.30,177.45,46.8,35.1,24.70,21.00,30.00,36.4,29.25,20.0,5.20,14.3,0.18)

STORAGE_DEVICE = {'elic':(0.95,0.95,0.04),'heat':(0.87,0.87,0.06),'cold':(0.88,0.88,0.01),'gas':(0.95,0.95,0.01)}

# 没有使用
DEVICE_INFO = {'ge':((2000,1,0,0),(460)),
                  'g2he':((10000,0.45,0.38)),
                  '2hc':((1500,5,4.4),(3000,1.8,2)),
                  'g2h':((6000,1)),
                  'e2h':((6000,0.97)),
                  'e2c':((1500,4)),
                  'h2c':((6000,1)),
                  'se':(0.95,0.95,0.04),'sh':(0.87,0.87,0.06),'sc':(0.88,0.88,0.01),'sg':(0.95,0.95,0.01)}


# 绿电出力 起始点7
PW = {'summer':(0.362267,0.322105,0.483797,0.478122,0.372791,0.29016,0.298849,0.266635,0.316447,0.37003,0.454681,0.403271,0.501074,0.763196,0.789281,0.9,0.806693,0.803224,0.535612,0.522578,0.498346,0.499053,0.426981,0.424977),
    'excessive':(0.362267,0.322105,0.483797,0.478122,0.372791,0.29016,0.298849,0.266635,0.316447,0.37003,0.454681,0.403271,0.501074,0.763196,0.789281,0.9,0.806693,0.803224,0.535612,0.522578,0.498346,0.499053,0.426981,0.424977),
    'winter':(0.362267,0.322105,0.483797,0.478122,0.372791,0.29016,0.298849,0.266635,0.316447,0.37003,0.454681,0.403271,0.501074,0.763196,0.789281,0.9,0.806693,0.803224,0.535612,0.522578,0.498346,0.499053,0.426981,0.424977)}
PV = {'summer':(0.243302478,0.35163601,0.439081313,0.515778361,0.507663984,0.527701222,0.507382318,0.456149073,0.361254604,0.257487657,0.155956059,0.06200547,0.002529001,0,0,0,0,0,0,0,0,0,0.02197594,0.117727392),
      'excessive':(0.140746695,0.26761255,0.399646177,0.466050032,0.520851944,0.507330279,0.447865296,0.379575778,0.288664485,0.173976489,0.058192392,0.001424311,0,0,0,0,0,0,0,0,0,0,8.97935E-05,0.038806281),
      'winter':(0.00199863,0.076562208,0.175235196,0.254095679,0.311657419,0.313392362,0.297876761,0.241588511,0.145693229,0.045261327,0.000386542,0,0,0,0,0,0,0,0,0,0,0,0,0)}

COP_COLD = 3.5
COP_HEAT = 2

PUE = 1.25
W_SUMMER_COLD = 0.2
W_SUMMER_OTHER = 0.05

W_EXCESSIVE_COLD = 0.18
W_EXCESSIVE_OTHER = 0.07

W_WINTER_COLD = 0.15
W_WINTER_HEAT = 0.05
W_WINTER_OTHER = 0.05
    

def get_load(load):
    load_9 = {'summer_workday':[[n*(1+W_SUMMER_OTHER) for n in load['workday']],[0]*24,[n*W_SUMMER_COLD*COP_COLD for n in load['workday']]],
            'summer_workend':[[n*(1+W_SUMMER_OTHER) for n in load['weekend']],[0]*24,[n*W_SUMMER_COLD*COP_COLD for n in load['weekend']]],
            'summer_holiday':[[n*(1+W_SUMMER_OTHER) for n in load['holiday']],[0]*24,[n*W_SUMMER_COLD*COP_COLD for n in load['holiday']]],
            'excessive_workday':[[n*(1+W_SUMMER_OTHER) for n in load['workday']],[0]*24,[n*W_EXCESSIVE_COLD*COP_COLD for n in load['workday']]],
            'excessive_workend':[[n*(1+W_SUMMER_OTHER) for n in load['weekend']],[0]*24,[n*W_EXCESSIVE_COLD*COP_COLD for n in load['weekend']]],
            'excessive_holiday':[[n*(1+W_SUMMER_OTHER) for n in load['holiday']],[0]*24,[n*W_EXCESSIVE_COLD*COP_COLD for n in load['holiday']]],
            'winter_workday':[[n*(1+W_SUMMER_OTHER) for n in load['workday']],[n*W_WINTER_HEAT*COP_HEAT for n in load['workday']],[n*W_WINTER_COLD*COP_COLD for n in load['workday']]],
            'winter_workend':[[n*(1+W_SUMMER_OTHER) for n in load['weekend']],[n*W_WINTER_HEAT*COP_HEAT for n in load['weekend']],[n*W_WINTER_COLD*COP_COLD for n in load['weekend']]],
            'winter_holiday':[[n*(1+W_SUMMER_OTHER) for n in load['holiday']],[n*W_WINTER_HEAT*COP_HEAT for n in load['holiday']],[n*W_WINTER_COLD*COP_COLD for n in load['holiday']]]}

    return load_9








