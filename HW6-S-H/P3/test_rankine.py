from rankine import Rankine

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
