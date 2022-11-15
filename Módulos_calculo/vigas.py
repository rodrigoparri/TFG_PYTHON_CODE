import math

class posTensionedBeam:

    # concrete properties
    fck = 35000
    fckt = 24700
    fctm = 3200
    fctmt = 2400
    Ect = 31300000
    Ec = 34000000
    Phi = 2  # creep coeffitient
    eps_cd0 = 0.41  # initial shrinkage strain
    # steel properties
    fpk = 1860000
    fpd = 1617391
    Ep = 195000000
    Es = 200000000
    # load at transfer kN/m2
    construction = 1
    # full loads kN/m2
    selfweight = 0
    partwalls = 1
    use_load = 0
    # instatant losses
    nu = 0.19
    gamma = 0.0075

    def __init__(self, h, b, l, e):

        self.h = h
        self.b = b
        self.l = l
        self. e = e

        self.Ab = self.h * self.b   # gross cross section
        self.Wb = self.h ** 2 * self.b / 6  # gross section modulus
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
        self.Mu = self.charac_load * self.l ** 2 / 8  # Max moment under chareacteristic load.
        self.Wmin = (1.1 * self.Mf - 0.9 * self.Mi) / (0.54 * self.fckt + 1.1 * self.fctm)

    def properties(self):
        return {"Ab": self.Ab,
               "Wb": self.Wb,
               "self weight": self.selfweight,
               "char load": self.charac_load,
               "frec tranfer load": self.frec_transfer_load,
               "frec full load": self.frec_full_load,
               "almost frecuent load": self.almostper_load,
               "Mi":self.Mi,
               "Mf":self.Mf,
               "Wmin": self.Wmin,
               "Pmin": self.Pmin(),
                "Pmax": self.Pmax(),
                "hflex": self.hflex(),


               }

    def hflex(self):
        # finder of the minimum heigh of the beam with b = 2h/3 that has a maximum deflection of l/400
        n = 0  # safety counter
        h = 0
        h_original = self.h
        while abs(self.h - h) >= 0.05 and n < 100:
            n +=1
            h = (93.5 * self.frec_full_load * self.l ** 3 / self.Ec) ** 0.25
            self.h = h

        a = round(h / 0.05, 0) * 0.05
        if a < h:
            a = a + 0.05
            h = a
            self.h = h_original
            return h
        else:
            h = a
            self.h = h_original
            return h

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

    def instantLosses(self, P, Ap):  # nu and gamma are the frictión coefficient and involuntary curvature respectively
        delta_Pfric = P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l ** 2 + self.gamma)))  # Friction losses
        delta_shortConcrete = (self.Ep / self.Ect * (P / self.Ab + P * self.e ** 2 / self.I)) * Ap  # Losses caused by concrete´s elastic shortening
        delta_Pjack = math.sqrt(2 * P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l ** 2 + self.gamma))) / self.l * 2 * 0.003 * self.Ep * Ap)
        # losses in the active jack.
        instantLosses = delta_Pfric + delta_shortConcrete + delta_Pjack
        return instantLosses

    def sectionHomo(self, Ap, dp, As1 = 0, d1 = 0, As2 = 0, d2 = 0):
        # As1 and As2 are the top and bottom passive reinforcement areas
        np = self.Ep / self.Ec
        ns = self.Es / self.Ec
        Ah = self.b * self.h + (np - 1) * Ap  # homogeneous cross section
        # position of the centroid from top fibre
        y = (self.b / 2 * (self.h * self.b) + dp * (ns - 1) * Ap + d1 * (ns - 1)* As1 + d2 * (ns -1) + As2) / Ah
        Ih = self.b * self.h ** 3 / 12 + Ap * (n-1) * dp ** 2 + d1 ** 2 * (ns - 1)* As1 + d2 ** 2 * (ns -1) + As2
        return Ah, y, Ih

    def cracked(self, P, Ap, M):
        sectionHomo = self.sectionHomo(Ap, self.h - 0.06)
        sigma_infmax = -P / sectionHomo[0] - P * e * (self.h - sectionHomo[1]) / sectionHomo[2] + M * (self.h - sectionHomo[1]) / sectionHomo[2]
        cracked = False  # check if max tensile tension is bigger than concrete´s tensile strenght
        if sigma_infmax >= self.fctm:
            cracked = True
            # S =

    def timedepLosses(self, Ap):
        ho = self.Ab / (self.h + self.b)
        kh = 0
        if ho <= 100:
            kh = 1
        elif 100< ho and ho <= 200:
            kh = 0.85
        elif 200< ho and ho <= 300:
            kh = 0.75
        else:
            kh = 0.7

        eps_cd = kh * self.eps_cd0
        eps_ca = 2.5 * (self.fck - 10) * (10 ** -6)
        eps_cs = eps_cd + eps_ca

    def Ap(self):
        trialAp = 0.000001
        Ap = 0

        while abs(Ap - trialAp) > 0.0000001:
            Ap = self.instantLosses(self.Pmin(), trialAp) / (0.1 * self.fpk)
            trialAp = Ap
        Ap_mm = Ap * 1000000

        return Ap, Ap_mm




if __name__ == "__main__":

    viga = posTensionedBeam(0.4, 0.3, 10, 0.055)
    # print(viga.properties())
    # print(viga.Pmin())
    # print(viga.Pmax())
    # print(viga.instantLosses(viga.Pmin(),0.0000568))
    print(viga.hflex())
    # h = 0.16
    # a = round(h / 0.05, 0) * 0.05
    # if a < h:
    #     a = a + 0.05
    #     h = a
    #     print(h)
    # else:
    #     h = a
    #     print(h)
    print(viga.properties())
    print(viga.Pmin())
    print(viga.Ap())