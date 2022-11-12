import math

class posTensionedBeam:

    # concrete properties
    fck = 35000
    fckt = 24700
    fctm = 3200
    fctmt = 2400
    Ect = 31300000
    Ec = 34000000
    # steel properties
    fpk = 1860000
    fpd = 1617391
    Ep = 195000000
    # load at transfer kN/m2
    construction = 1
    # full loads kN/m2
    selfweight = 0
    partwalls = 1
    use_load = 0
    # instatant losses
    nu = 0.19
    gamma = 0.0075

    def __init__(self, h, b, l, e,):

        self.h = h
        self.b = b
        self.l = l
        self. e = e

        self.Ab = self.h * self.b   # gross cross section
        self.Wb = self.b * self.h ** 2 / 6  # gross section modulus
        self.I = self.b * self.h ** 3 / 12  #gross moment of inertia
        self.selfweight = self.Ab * 24

        if self.l >= 7:
            self.use_load = 5
        else:
            self.use_load = 2

        self.charac_load = 1.35 * (self.selfweight + self.partwalls) + 1.5 * self.use_load
        self.frec_transfer_load = self.selfweight + self.construction * 0.7
        self.frec_full_load = self.selfweight + self.partwalls + 0.7 * self.use_load
        self.almostper_load = self.selfweight + self.partwalls + 0.6 * self.use_load
        self.Mi = self.frec_transfer_load * self.l ** 2 / 8  # Max initial moment under loads at transfer.
        self.Mf = self.frec_full_load * self.l ** 2 / 8  # Max moment under full loads.

    def Pmin(self):
        # Pmin will always be determined by the intersection of lines 4 (tension under full loads) and P*e
        Pmin = (-self.fctm * self.Wb / 0.9 + self.Mf / 0.9) * (1 / (self.e + self.h / 6))
        return Pmin

    def Pmax(self):
        Pmax = 0
        # Pmax will be the minimun between the intersection of both lines 1 and 2 with P*e
        Pmax1 = (self.fctmt * self.Wb / 1.1 + self.Mi / 1.1) * (1/(self.e - self.h / 6))
        Pmax2 = (0.6 * self.fckt * self.Wb / 1.1 + self.Mi / 1.1) * (1 / (self.e + self.h / 6))

        if Pmax1 > 0 and Pmax2 > 0:
            Pmax = min(Pmax1, Pmax2)
        elif Pmax1 < 0:
            Pmax = Pmax2
        elif Pmax2 < 0:
            Pmax = Pmax1
        return Pmax

    def instanLosses(self, P, Ap):  # nu and gamma are the frictión coefficient and involuntary curvature respectively
        delta_Pfric = P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l ** 2 + self.gamma)))  # Friction losses
        delta_shortConcrete = (self.Ep / self.Ect * (P / self.Ab + P * self.e ** 2 / self.I)) * Ap  # Losses caused by concrete´s elastic shortening
        delta_Pjack = math.sqrt(2 * P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l ** 2 + self.gamma))) / self.l * 2 * 0.003 * self.Ep * Ap)
        # losses in the active jack.
        instantLosses = delta_Pfric + delta_shortConcrete + delta_Pjack
        return instantLosses


    def debug(self):
        print({"Ab": self.Ab,
               "Wb": self.Wb,
               "self weight": self.selfweight,
               "char load": self.charac_load,
               "frec tranfer load": self.frec_transfer_load,
               "frec full load": self.frec_full_load,
               "almost frecuent load": self.almostper_load,
               "Mi":self.Mi,
               "Mf":self.Mf
               })



if __name__ == "__main__":

    viga = posTensionedBeam(0.2, 0.15, 5, 0.028)
    viga.debug()
    print(viga.Pmin())
    print(viga.Pmax())
    print(viga.instanLosses(viga.Pmin(),0.0000568))



