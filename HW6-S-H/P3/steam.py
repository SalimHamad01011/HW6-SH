import numpy as np
from scipy.interpolate import griddata


class Steam:
    def __init__(self, pressure, T=None, x=None, v=None, h=None, s=None, name=None):
        self.p = pressure
        self.T = T
        self.x = x
        self.v = v
        self.h = h
        self.s = s
        self.name = name
        self.region = None
        if T is None and x is None and v is None and h is None and s is None:
            return
        else:
            self.calculate_properties()

    def calculate_properties(self):
        try:
            # Read in the thermodynamic data from the saturated water table file
            ts, ps, hfs, hgs, sfs, sgs, vfs, vgs = np.loadtxt('sat_water_table.txt', unpack=True, skiprows=1)

            # Assuming the superheated properties file has columns: Temperature, Enthalpy, Entropy, Pressure
            tcol, hcol, scol, pcol = np.loadtxt('superheated_water_table.txt', unpack=True, skiprows=1)

            R = 8.314 / (18 / 1000)
            Pbar = self.p / 100

            # Get saturated properties
            Tsat = float(griddata(ps, ts, Pbar))
            hf = float(griddata(ps, hfs, Pbar))
            hg = float(griddata(ps, hgs, Pbar))
            sf = float(griddata(ps, sfs, Pbar))
            sg = float(griddata(ps, sgs, Pbar))
            vf = float(griddata(ps, vfs, Pbar))
            vg = float(griddata(ps, vgs, Pbar))

            self.hf = hf

            if self.T is not None:
                if self.T > Tsat:
                    self.region = 'Superheated'
                    self.h = float(griddata((tcol, pcol), hcol, (self.T, Pbar)))
                    self.s = float(griddata((tcol, pcol), scol, (self.T, Pbar)))
                    self.x = 1.0
                    TK = self.T + 273.14
                    self.v = R * TK / (self.p * 1000)
            elif self.x is not None:
                self.region = 'Saturated'
                self.T = Tsat
                self.h = hf + self.x * (hg - hf)
                self.s = sf + self.x * (sg - sf)
                self.v = vf + self.x * (vg - vf)
            elif self.h is not None:
                self.x = (self.h - hf) / (hg - hf)
                if self.x <= 1.0:
                    self.region = 'Saturated'
                    self.T = Tsat
                    self.s = sf + self.x * (sg - sf)
                    self.v = vf + self.x * (vg - vf)
                else:
                    self.region = 'Superheated'
                    self.T = float(griddata((hgs, ps), ts, (self.h, Pbar)))
                    self.s = float(griddata((hgs, ps), sgs, (self.h, Pbar)))
            elif self.s is not None:
                self.x = (self.s - sf) / (sg - sf)
                if self.x <= 1.0:
                    self.region = 'Saturated'
                    self.T = Tsat
                    self.h = hf + self.x * (hg - hf)
                    self.v = vf + self.x * (vg - vf)
                else:
                    self.region = 'Superheated'
                    self.T = float(griddata((sgs, ps), ts, (self.s, Pbar)))
                    self.h = float(griddata((sgs, ps), hgs, (self.s, Pbar)))

        except FileNotFoundError:
            print("Error: Steam table file not found!")

    def print_properties(self):
        print('Name: ', self.name)
        if self.x < 0.0:
            print('Region: compressed liquid')
        else:
            print('Region: ', self.region)
        print('p = {:0.2f} kPa'.format(self.p))
        if self.x >= 0.0: print('T = {:0.1f} degrees C'.format(self.T))
        print('h = {:0.2f} kJ/kg'.format(self.h))
        if self.x >= 0.0:
            print('s = {:0.4f} kJ/(kg K)'.format(self.s))
            if self.region == 'Saturated': print('v = {:0.6f} m^3/kg'.format(self.v))
            if self.region == 'Saturated': print('x = {:0.4f}'.format(self.x))
        print()


def main():
    # Example usage
    inlet = Steam(7350, name='Turbine Inlet')
    inlet.x = 0.9
    inlet.calculate_properties()
    inlet.print_properties()

    h1 = inlet.h
    s1 = inlet.s
    print(h1, s1, '\n')

    outlet = Steam(100, s=inlet.s, name='Turbine Exit')
    outlet.print_properties()

    another = Steam(8575, h=2050, name='State 3')
    another.print_properties()
    yet_another = Steam(8575, h=3125, name='State 4')
    yet_another.print_properties()


if __name__ == "__main__":
    main()
