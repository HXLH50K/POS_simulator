from abc import ABCMeta, abstractmethod

def sanitised_input(prompt, type_=None, min_=None, max_=None, range_=None):
    if min_ is not None and max_ is not None and max_ < min_:
        raise ValueError("min_ must be less than or equal to max_.")
    while True:
        ui = input(prompt)
        if type_ is not None:
            try:
                ui = type_(ui)
            except ValueError:
                print("Input type must be {0}.".format(type_.__name__))
                continue
        if max_ is not None and ui > max_:
            print("Input must be less than or equal to {0}.".format(max_))
        elif min_ is not None and ui < min_:
            print("Input must be greater than or equal to {0}.".format(min_))
        elif range_ is not None and ui not in range_:
            if isinstance(range_, range):
                template = "Input must be between {0.start} and {0.stop}."
                print(template.format(range_))
            else:
                template = "Input must be {0}."
                if len(range_) == 1:
                    print(template.format(*range_))
                else:
                    print(template.format(" or ".join((", ".join(
                        map(str, range_[:-1])), str(range_[-1])))))
        else:
            return ui

class CashMode_Base(object):
    __metaclass__ = ABCMeta
    __name = None
    def __init__(self):
        self.final_price = None
    
    def name(self) -> str:
        return self.__name

    @abstractmethod
    def set_value(self):
        return

    @abstractmethod
    def accept_cash(self):
        return
 
class CashMode_Normal(CashMode_Base):
    _CashMode_Base__name = "正常收费"
    def __init__(self, money):
        self.money = money

    def accept_cash(self):
        self.final_price = self.money
        return self.final_price

class CashMode_Return(CashMode_Base):
    _CashMode_Base__name = "满减"
    def __init__(self, money):
        self.money = money
        self.return_condition = 1000
        self.return_money = 0
    
    def set_value(self):
        print("输入满减标准：")
        self.return_condition = sanitised_input("满x: ", float, min_ = 0)
        self.return_money = sanitised_input("减y: ", 
            float, min_ = 0, max_ = self.return_condition)

    def accept_cash(self):
        return_times = self.money//self.return_condition
        while return_times>0:
            self.money -= self.return_money
            return_times -= 1
        self.final_price = self.money
        return self.final_price

class CashMode_Rebate(CashMode_Base):
    _CashMode_Base__name = "打折"
    def __init__(self, money):
        self.money = money
        self.rebate = 1
    
    def set_value(self):
        self.rebate = sanitised_input("输入折扣比例: ", 
            float, min_ = 0, max_ = 1)

    def accept_cash(self):
        self.final_price = self.money * self.rebate
        return self.final_price

class CashMode_Addtax(CashMode_Base):
    _CashMode_Base__name = "加税"
    def __init__(self, money):
        self.money = money
        self.tax = 0

    def set_value(self):
        self.tax = sanitised_input("输入税率: ", float, min_ = 0)

    def accept_cash(self):
        self.final_price = self.money * (1 + self.tax)
        return self.final_price

class POS(object):
    def __init__(self):
        self.m_cashmodes = []
    
    def registe(self, a_cashmode: CashMode_Base):
        if a_cashmode is None:
            return
        self.m_cashmodes.append(a_cashmode)

    def unregiste(self, a_cashmode: CashMode_Base):
        if a_cashmode is None:
            return
        self.del_cashmode(a_cashmode.name())

    def get_cashmode(self, a_cashmodename: str):
        for x in self.m_cashmodes:
            if x.name() == a_cashmodename:
                return x
        return None

    def del_cashmode(self, a_cashmodename: str):
        for (i,x) in enumerate(self.m_cashmodes):
            if x.name() == a_cashmodename:
                del self.m_cashmodes[i]
                break
        return None

    def get_result(self, money):
        return self.cash_strategy.accept_cash(money)  

def client():
    price = sanitised_input("输入商品单价:", float, min_ = 0)
    number = sanitised_input("输入商品数量:", int, min_ = 0)
    total = price*number

    cashmode_select = {}
    cashmodes = POS()
    cashmodes.registe(CashMode_Normal(money = total))
    cashmodes.registe(CashMode_Return(money = total))
    cashmodes.registe(CashMode_Rebate(money = total))
    cashmodes.registe(CashMode_Addtax(money = total))
    for (i,x) in enumerate(cashmodes.m_cashmodes):
        print("{}: {}".format(i+1, x.name()))
        cashmode_select[i+1] = x

    cashmode_index = sanitised_input("选择收费方式(1~%d): " 
        % len(cashmode_select), 
        int, min_ = 1, max_ = len(cashmode_select))
    cashmode_select[cashmode_index].set_value()
    return total, cashmode_select[cashmode_index].accept_cash()

if __name__ == '__main__':
    res = client()
    print("原价: {}\n实收: {}".format(res[0], res[1]))