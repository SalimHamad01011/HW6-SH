from steam import Steam  # Assuming Steam class is in the steam.py file

class Rankine:
    def __init__(self, p_low=8, p_high=8000, t_high=None, name='Rankine Cycle'):
        self.p_low = p_low
        self.p_high = p_high
        self.t_high = t_high
        self.name = name
        self.efficiency = None
        self.turbine_work = 0
        self.pump_work = 0
        self.heat_added = 0
        self.state1 = None
        self.state2 = None
        self.state3 = None
        self.state4 = None

    def calc_efficiency(self):
        try:
            # Calculate the 4 states
            # State 1: Turbine inlet (p_high, t_high) superheated or saturated vapor
            if self.t_high is None:
                self.state1 = Steam(self.p_high, x=1, name='Turbine Inlet')
            else:
                self.state1 = Steam(self.p_high, T=self.t_high, name='Turbine Inlet')

            # State 2: Turbine exit (p_low, s=s_turbine inlet) two-phase
            self.state2 = Steam(self.p_low, s=self.state1.s, name='Turbine Exit')

            # State 3: Pump inlet (p_low, x=0) saturated liquid
            self.state3 = Steam(self.p_low, x=0, name='Pump Inlet')

            # State 4: Pump exit (p_high, s=s_pump_inlet) typically sub-cooled, but estimate as saturated liquid
            self.state4 = Steam(self.p_high, s=self.state3.s, name='Pump Exit')
            self.state4.h = self.state3.h + self.state3.v * (self.p_high - self.p_low)

            self.turbine_work = self.state1.h - self.state2.h
            self.pump_work = self.state4.h - self.state3.h
            self.heat_added = self.state1.h - self.state4.h
            self.efficiency = 100.0 * (self.turbine_work - self.pump_work) / self.heat_added
            return self.efficiency
        except Exception as e:
            print(f"Error in calc_efficiency: {e}")
            return None

    def print_summary(self):
        if self.efficiency is None:
            self.calc_efficiency()
        print('Cycle Summary for: ', self.name)
        print('\tEfficiency: {:0.3f}%'.format(self.efficiency))
        print('\tTurbine Work: {:0.3f} kJ/kg'.format(self.turbine_work))
        print('\tPump Work: {:0.3f} kJ/kg'.format(self.pump_work))
        print('\tHeat Added: {:0.3f} kJ/kg'.format(self.heat_added))
        print(self.state1)
        print(self.state2)
        print(self.state3)
        print(self.state4)

def main():
    rankine1 = Rankine(p_low=8, p_high=8000, t_high=None, name='Rankine Cycle Case i')
    eff1 = rankine1.calc_efficiency()
    print("Case i Efficiency:", eff1)
    rankine1.print_summary()

    rankine2 = Rankine(p_low=8, p_high=8000, t_high=None, name='Rankine Cycle Case ii')
    eff2 = rankine2.calc_efficiency()
    print("Case ii Efficiency:", eff2)
    rankine2.print_summary()

if __name__ == "__main__":
    main()
