import math

class posTensionedIsoBeam:

    # concrete properties
    fck = 35
    fckt = 24.7
    fctm = 3.2
    fctmt = 2.4
    Ect = 31300
    Ec = 34000
    Phi = 2  # creep coeffitient
    eps_cd0 = 0.0041  # initial shrinkage strain
    # Active steel properties
    fpk = 1860
    fpd = 1617.391
    Ep = 195000
    #  Passive steel properties
    fyk = 500
    Es = 200000
    # load at transfer N/mm2
    construction = 1
    # full loads N/mm
    selfweight = 0
    partwalls = 1
    use_load = 0
    # instatant losses
    nu = 0.19
    gamma = 0.75 * 1e-5
    # ducts
    ducts = {
            60:2400,
            75:3800,
            85:5000,
            95:6400,
            105:7900,
            120:10400,
            130:12300,
            145:15400
            }
    def __init__(self, h, b, e, l):

        self.h = h
        self.b = b
        self.l = l
        self. e = e
        self.dp = self.h / 2 + self.e
        self.rec = 30  # concrete cover

        self.Ab = self.h * self.b   # gross cross section
        self.Wb = self.h ** 2 * self.b / 6  # gross section modulus
        self.I = self.b * self.h ** 3 / 12  #gross moment of inertia
        self.selfweight = self.Ab * 24 * 1e-6

        # N/mm
        if self.l >= 7000:
            self.use_load = 5
        else:
            self.use_load = 2

        self.charac_load = 1.35 * (self.selfweight + self.partwalls) + 1.5 * self.use_load
        self.frec_transfer_load = self.selfweight + self.construction * 0.7
        self.frec_full_load = self.selfweight + self.partwalls + 0.7 * self.use_load
        self.almostper_load = self.selfweight + self.partwalls + 0.6 * self.use_load
        self.Mi = self.frec_transfer_load * self.l ** 2 / 8  # Max initial moment under loads at transfer.
        self.Mf = self.frec_full_load * self.l ** 2 / 8  # Max moment under full loads.
        self.Me = self.almostper_load * self.l ** 2 / 8  # Max moment under almost permanent loads
        self.Mu = self.charac_load * self.l ** 2 / 8  # Max moment under characteristic load.
        self.Wmin = (1.1 * self.Mf - 0.9 * self.Mi) / (0.54 * self.fckt + 1.1 * self.fctm)

    def properties(self):
        Pmin = self.Pmin()
        Pmax = self.Pmax()
        Ap = self.Ap(Pmin)
        instantLosses = self.instantLosses(Ap, Pmin)
        timedepLosses = self.timedepLosses()

        return {"Ab mm2": self.Ab,
                "Wb cm3": self.Wb * 1e-3,
                "hflex mm": self.hflex(),
                "self weight kN/m": self.selfweight,
                "char load kN/m": self.charac_load,
                "frec tranfer load kN/m": self.frec_transfer_load,
                "frec full load kN/m": self.frec_full_load,
                "almost frecuent load kN/m": self.almostper_load,
                "Mi mkN":self.Mi * 1e-6,
                "Mf nKN":self.Mf * 1e-6,
                "Wmin cm3": self.Wmin * 1e-3,
                "Pmin kN": self.Pmin() * 1e-3,
                "Pmax kN": self.Pmax() * 1e-3,
                "Ap mm2": Ap,
                "instantLosses kN": instantLosses * 1e-3,
                "timedepLosses kN": timedepLosses * 1e-3
               }

    def hflex(self):
        # finder of the minimum heigh of the beam with b = 2h/3 that has a maximum deflection of l/400
        n = 0  # safety counter
        h = 0
        h_original = self.h
        while abs(self.h - h) >= 50 and n < 100:
            n +=1
            h = (93.5 * self.frec_full_load * self.l ** 3 / self.Ec) ** 0.25
            self.h = h

        a = round(h / 50) * 50
        if a < h:
            a = a + 50
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

    def equivalentLoad(self, P):
        q_eqv = P * self.e * 8 / self.l ** 2
        return q_eqv

    def sectionHomo(self, Ap, dp, As1 = 0, d1 = 0, As2 = 0, d2 = 0):
        # As1 and As2 are the bottom and top passive reinforcement areas
        np = self.Ep / self.Ec
        ns = self.Es / self.Ec
        Ah = self.b * self.h + (np - 1) * Ap  # homogeneous cross section
        # position of the centroid from top fibre
        y = (self.h / 2 * (self.h * self.b) + dp * (ns - 1) * Ap + d1 * (ns - 1)* As1 + d2 * (ns -1) + As2) / Ah
        Ih = self.b * self.h ** 3 / 12 + Ap * (np-1) * dp ** 2 + d1 ** 2 * (ns - 1)* As1 + d2 ** 2 * (ns -1) * As2
        return Ah, y, Ih

    def cracked(self, P, Ap, M):
        sectionHomo = self.sectionHomo(Ap, self.h - 0.06)
        sigma_infmax = -P / sectionHomo[0] - P * e * (self.h - sectionHomo[1]) / sectionHomo[2] + M * (self.h - sectionHomo[1]) / sectionHomo[2]
        cracked = False  # check if max tensile tension is bigger than concrete´s tensile strenght
        if sigma_infmax >= self.fctm:
            cracked = True
            # S =

    def instantLosses(self, P, Ap):  # nu and gamma are the frictión coefficient and involuntary curvature respectively
        delta_Pfric = P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l ** 2 + self.gamma)))  # Friction losses
        delta_shortConcrete = self.Ep / self.Ect * (P / self.Ab + P * self.e ** 2 / self.I) * Ap  # Losses caused by concrete´s elastic shortening
        alpha = 2 * P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l **2 + self.gamma))) / self.l
        L_c = math.sqrt(2 * 3 * self.Ep * Ap / alpha)
        # delta_Pjack = math.sqrt(2 * 3 * alpha * self.Ep * Ap)
        delta_Pjack = alpha * L_c
        # losses in the active jack.
        instantLosses = delta_Pfric + delta_shortConcrete + delta_Pjack
        return instantLosses

    def timedepLosses(self):
        Pmin = self.Pmin()
        M = self.Me
        phi = 2
        ho = self.Ab / (self.h + self.b)
        kh = 0
        Ap = self.Ap(Pmin)
        sectionHomo = self.sectionHomo(Ap, self.h / 2 + self.e)  # Ab, y, Ib
        relaxation = 0

        if ho <= 200:
            kh = 1
        elif 200 < ho and ho <= 300:
            kh = 0.85
        elif 300 < ho and ho <= 500:
            kh = 0.75
        elif ho > 500:
            kh = 0.7

        betha_ds = 23 / (23 * 0.04 * ((ho) ** 3) ** 0.5)

        eps_cd = kh * betha_ds * self.eps_cd0  # drying strain
        eps_ca = betha_ds * 2.5 * (self.fck - 10) * (10 ** -6)  # shrinkage strain
        eps_cs = eps_cd + eps_ca # total shrinkage strain

        # calculate stress with Ep*epsp calculate eps with the gross cross section and multiply by 2,9 to account for relaxation
        initial_tension = self.Ep / self.Ec * (- Pmin / sectionHomo[0] - (Pmin * self.e ** 2 + M * self.e ) / sectionHomo[2] )
        initial_tension = abs(initial_tension)

        if initial_tension >= .6 * self.fpk:
            relaxation = .015
        elif initial_tension >= 0.7 * self.fpk:
            relaxation = .025
        elif initial_tension >= .8 * self.fpk:
            relaxation = .045

        sigma_pr = initial_tension * (1 - 3 * relaxation)
        sigma_cQp = initial_tension / self.Ep

        numerator = Ap * eps_cs * self.Ep + .8 * (initial_tension- sigma_pr) + self.Ep / self.Ec * phi * sigma_cQp
        denominator = 1 + self.Ep * Ap / (self.Ec * self.Ab) * (1 + self.Ab / self.I * sectionHomo[1] ** 2) * (1 + .8 * phi)

        timedepLosses = numerator / denominator
        return timedepLosses

    def Ap(self, P):
        trialAp = 10  # trialAp must always be bigger than the reference value in the while loop
        Ap = 0
        n = 0
        Pmin = P

        while n < 15:  # reference value.
            Ap = self.instantLosses(Pmin, trialAp) / (0.1 * self.fpk)
            trialAp = Ap
            n += 1

        return Ap

    def checkInstDeflect(self, Ap, EqLoad):   # checking max isostatic deflection
        sectionHomo = self.sectionHomo(Ap, self.h / 2 + self.e )
        deflection = 5/384 * (self.frec_full_load - EqLoad) * self.l ** 3 / (self.Ec * sectionHomo[2])

        if deflection < self.l / 400:
            return True, deflection    # a true value stands for a correct deflection
        else:
            return False, deflection   # a false value stands for an incorrect deflection

    def checkELU(self, Ap, As1 = 0, As2 = 0):

        x = 1.5 * Ap * self.fpk / (1.15 * .8 * self.b * self.fck)  # check where the neutral fibre is countting on the existing Ap
        M_front  = Ap * self.fpk / 1.15 * (self.dp - 0.8 * x / 2)  # Moment generated by the active reinforcement after yielding

        if M_front < self.Mu:  # check if ELU moment is bigger than the beam´s strenght
            while self.Mu - M_front > 0.1:

                increAs1 = (self.Mu - M_front) * 1.15 / ((self.h - self.rec) * self.fyk) # passive reinforcement necessar
                x = 1.5 (Ap * self.fpk + increAs1 * self.fyk) / (1.15 * 300 * .8 * self.fck) # recalculate neutral fibre.
                M_front = Ap * self.fpk / 1.15 * self.dp + increAs1 * self.fyk / 1.15 * (self.h - self.rec) - 0.32 * x ** 2 * self.b * self.fck / 3

                if x / self.dp < 0.335:  ## revise this. postensioned strain needs to be checked.
                    increAs2 =
                    print("Ap no plastified")


        Ms1 = As1 * self.fpk / 1.15 * (self.h - .03)  # Moment generated by the bottom reinforcement
        Ms2 = As2 * self.fpk / 1.15 * 0.03  # Momente generated by the top reinforcement
        Mc = 0.32 * x ** 2 * self.b * self.fck / 1.5  # Moment generated by concrete
        M_front = Mp + Ms1 - Ms2 - Mc  # total moment



        return M_front

class reinforcedIsoBeam:

    def __init__(self):
        pass


if __name__ == "__main__":

    viga = posTensionedIsoBeam(400, 300, 140, 10000)
    Pmin = viga.Pmin()
    Ap = viga.Ap(Pmin)
    print(Ap)
    # print(viga.instantLosses(Pmin, Ap))
    # print(viga.properties())
    print(viga.checkELU(Ap))

