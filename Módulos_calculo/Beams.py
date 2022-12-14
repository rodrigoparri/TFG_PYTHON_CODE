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
    eps_cd0 = 0.00041  # initial shrinkage strain
    reca = 40  # concrete cover
    # Active steel properties
    fpk = 1860
    # fpd = 1617.391
    fbpt = 4.8
    Ep = 195000
    #  Passive steel properties
    fyk = 500
    Es = 200000
    recp = 30
    # load at transfer N/mm2
    construction = 1
    # full loads N/mm
    selfweight = 0
    partwalls = 1
    use_load = 0
    flooring = 1.5
    # instatant losses
    nu = 0.19
    gamma = 0.75 * 1e-5
    # ducts D:area
    ducts = {
        60: 2400,
        75: 3800,
        85: 5000,
        95: 6400,
        105: 7900,
        120: 10400,
        130: 12300,
        145: 15400
    }
    # bars D:area
    bars = {
        6: 28.27,
        8: 50.27,
        10: 78.54,
        12: 113.10,
        14: 153.94,
        16: 201.06,
        20: 314.16,
        25: 490.87,
        32: 804.25,
        40: 1256.64
    }

    def __init__(self, l):

        self.l = l
        height = int(l / 1250) * 50
        if height < l / 25:
            self.h = height + 50
        else:
            self.h = height

        width = int(self.h * 2 / 150) * 50
        if width < (self.h * 2 / 3):
            self.b = width + 50
        else:
            self.b = width

        self.e = self.h / 2 - (self.reca + list(self.ducts.keys())[0] / 2)
        self.dp = self.h / 2 + self.e

        self.Ab = self.h * self.b  # gross cross section
        self.Wb = self.h ** 2 * self.b / 6  # gross section modulus
        self.I = self.b * self.h ** 3 / 12  # gross moment of inertia
        self.selfweight = self.Ab * 24 * 1e-6

        # N/mm
        if self.l >= 7000:
            self.use_load = 5
        else:
            self.use_load = 2

        self.charac_load = 1.35 * (self.selfweight + self.partwalls + self.flooring) + 1.5 * self.use_load
        self.frec_transfer_load = self.selfweight + + self.flooring + self.construction * 0.7
        self.frec_full_load = self.selfweight + self.flooring + self.partwalls + 0.7 * self.use_load
        self.almostper_load = self.selfweight + self.flooring + self.partwalls + 0.6 * self.use_load
        self.Mi = self.frec_transfer_load * self.l ** 2 / 8  # Max initial moment under loads at transfer.
        self.Mf = self.frec_full_load * self.l ** 2 / 8  # Max moment under full loads.
        self.Me = self.almostper_load * self.l ** 2 / 8  # Max moment under almost permanent loads
        self.Mu = self.charac_load * self.l ** 2 / 8  # Max moment under characteristic load.
        self.Wmin = (1.1 * self.Mf - 0.9 * self.Mi) / (0.54 * self.fckt + 1.1 * self.fctm)

        if self.h < self.hflex()[0]:  # check if the selected h is smallet than the required one by deflection considerations
            self.h = self.hflex()[0]

        if self.b < self.hflex()[1]:
            self.b = self.hflex()[1]

    def __str__(self) -> str:
        text = f"IsoPB{self.l / 1000}"
        return text

    def Properties(self) -> dict:
        Pmin = self.Pmin()
        Pmax = self.Pmax()
        Ap = self.Ap(Pmin)
        Imin = self.Iflex()
        instantLosses = self.instantLosses(Pmin, Ap)
        timedepLosses = self.timedepLosses(Pmin, Ap)

        return {"Ab mm2": self.Ab,
                "h mm": self.h,
                "b mm": self.b,
                "Wb cm3": self.Wb * 1e-3,
                "Wmin cm3": self.Wmin * 1e-3,
                "Ib cm4": self.I * 1e-4,
                "Imin cm4": Imin * 1e-4,
                "hflex mm": self.hflex(),
                "self weight kN/m": self.selfweight,
                "char load kN/m": self.charac_load,
                "frec tranfer load kN/m": self.frec_transfer_load,
                "frec full load kN/m": self.frec_full_load,
                "almost frecuent load kN/m": self.almostper_load,
                "Mi mkN": self.Mi * 1e-6,
                "Mf nKN": self.Mf * 1e-6,
                "Pmin kN": Pmin * 1e-3,
                "Pmax kN": Pmax * 1e-3,
                "Ap mm2": Ap,
                "instantLosses kN": instantLosses * 1e-3,
                "timedepLosses kN": timedepLosses * 1e-3
                }
    @staticmethod
    def aprox(value, div):
        """
        aproximate any continuous value to a set of discrete equally spaced values.
        :param value: value is the value you want to aproximate to an infinite set of discrete equally spaced values
        :param div: is the distances between those discrete values
        :return: the value within the set just above it
        """
        a = int(value / div) * div
        a += div

        return a


    def hflex(
            self):  # COMPROBAR QUE LA SALIDA DE HFLEX ES IGUAL A LAS H Y B ELEGIDAS SI SON MAYORES PONER LAS DE HFLEX.
        # finder of the minimum heigh of the beam with b = 2h/3 that has a maximum deflection of l/400
        h = pow(93.75 * self.frec_full_load * self.l ** 3 / self.Ec, 0.25)
        b = 2 / 3 * h
        h = self.aprox(h, 50)
        b = self.aprox(b, 50)

        return h, b

    def Iflex(self):
        I = 5 * 400 * self.frec_full_load * pow(self.l, 3) / (384 * self.Ec)
        return I

    def Pmin(self):  # Magnel diagram
        # Pmin will always be determined by the intersection of lines 4 (tension under full loads) and P*e
        Pmin = (-self.fctm * self.Wb / 0.9 + self.Mf / 0.9) * (1 / (self.e + self.h / 6))
        return Pmin

    def Pmax(self):  # Magnel diagram
        Pmax = 0
        # Pmax will be the minimun between the intersection of both lines 1 and 2 with P*e
        Pmax1 = (self.fctmt * self.Wb / 1.1 + self.Mi / 1.1) * (1 / (self.e - self.h / 6))
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

    def sectionHomo(self, Ap, As1=0, d1=0, As2=0, d2=0):
        # As1 and As2 are the bottom and top passive reinforcement areas
        np = self.Ep / self.Ec
        ns = self.Es / self.Ec
        Ah = self.b * self.h + (np - 1) * Ap  # homogeneous cross section
        # position of the centroid from top fibre
        y = (self.h / 2 * (self.h * self.b) + self.dp * (ns - 1) * Ap + d1 * (ns - 1) * As1 + d2 * (ns - 1) + As2) / Ah
        Ih = self.b * self.h ** 3 / 12 + Ap * (np - 1) * self.dp ** 2 + d1 ** 2 * (ns - 1) * As1 + d2 ** 2 * (
                    ns - 1) * As2
        return Ah, y, Ih

    def cracked(self, P, Ap, As1=0, As2=0, Dp=0, Ds1=0, Ds2=0):# D=diameter. is convenient to use P after all losses have been applied.

        # tau_bms1 = 7.84 - .12 * Ds1  # transmision stress for passive reinforcement
        # tau_bms2 = 7.84 - .12 * Ds2

        x = self.h  # stablish x=dp to start iterating until an equilibrium solution is found.

        # first of all we need to check for equilibrium of forces in order to calculate the depth of the neutral fibre
        eps_c = -1 * 0.6 * self.fck / self.Ec
        Uc = 1 / 2 * eps_c * self.Ec * x * self.b  # Concrete force

        Us2 = As2 * self.Es * eps_c * (x - self.recp) / x  # top reinforcement force

        # strain components of the active reinforcement

        eps_p1 = P / (self.Ep * Ap)
        eps_p2 = 1 / self.Ec * (P / self.Ab + P * self.e ** 2 / self.I)
        eps_p3 = eps_c * (1 - self.dp / x)
        Up = Ap * self.Ep * (eps_p1 + eps_p2 + eps_p3)  # active reinforcement force

        eps_s1 = eps_c * (1 - (self.h - self.recp) / x)
        Us1 = As1 * self.Es * (eps_s1)  # bottom passive reinforcement force.

        M = Up * self.dp + Us1 * (self.h - self.recp) - Uc * x / 3 - Us2 * (self.recp)
        n = 0
        # "Up" might not be big enough to equilibrate the compression forces for the given strain plane.
        # so added with its sign while the sum of all the forces is negative. the depth of the compresion block
        # will continue to decrease as active reinforcement strain will continue to grow
        while Uc + Us2 + Up + Us1 < 0 or M < self.Mf and n < 100: # while compresion is too high or moment equilibrium is not met.
            n += 1  # Security counter
            x -= 1  # x is reduced by 5 mm in each round.

            eps_c = -1 * 0.6 * self.fck / self.Ec
            Uc = 1 / 2 * eps_c * x * self.b

            Us2 = As2 * self.Es * eps_c * (x - self.recp) / x

            eps_p1 = P / (self.Ep * Ap)
            eps_p2 = 1 / self.Ec * (P / self.Ab + P * self.e ** 2 / self.I)
            eps_p3 = eps_c * (self.dp / x - 1)
            Up = Ap * self.Ep * (eps_p1 + eps_p2 + eps_p3)

            eps_s2 = eps_c * ((self.h - self.recp) / x - 1)
            Us1 = As1 * self.Es * eps_s2

            M = Up * self.dp + Us1 * (self.h - self.recp) - Uc * x / 3 - Us2 * (self.recp)

        Ap_13 = abs(self.aprox(Ap, 98.74))
        Ap_15 = abs(self.aprox(Ap, 140))

        n_13 = Ap_13 / 98.74
        n_15 = Ap_15 / 140


        Act = (self.h - x) * self.b
        # S = 0.25 * self.fctm / 4.8 * Act *
        return x, n

    def instantLosses(self, P, Ap):  # nu and gamma are the frictión coefficient and involuntary curvature respectively
        delta_Pfric = P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l ** 2 + self.gamma)))  # Friction losses
        delta_shortConcrete = self.Ep / self.Ect * (
                P / self.Ab + P * self.e ** 2 / self.I) * Ap  # Losses caused by concrete´s elastic shortening
        alpha = 2 * P * (1 - math.exp(-self.nu * self.l * (8 * self.e / self.l ** 2 + self.gamma))) / self.l
        L_c = math.sqrt(2 * 3 * self.Ep * Ap / alpha)
        # delta_Pjack = math.sqrt(2 * 3 * alpha * self.Ep * Ap)
        delta_Pjack = alpha * L_c
        # losses in the active jack.
        instantLosses = delta_Pfric + delta_shortConcrete + delta_Pjack
        return instantLosses

    def timedepLosses(self, P, Ap):

        M = self.Me
        phi = 2
        ho = self.Ab / (self.h + self.b)
        kh = 0
        sectionHomo = self.sectionHomo(Ap)  # Ab, y, Ib
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

        # eps_cd = kh * betha_ds * self.eps_cd0  # drying strain
        eps_cd = kh * self.eps_cd0
        # eps_ca = betha_ds * 2.5 * (self.fck - 10) * (10 ** -6)  # shrinkage strain
        eps_ca = 2.5 * (self.fck - 10) * (10 ** -6)
        eps_cs = eps_cd + eps_ca  # total shrinkage strain

        # calculate stress with Ep*epsp calculate eps with the gross cross section and multiply by 2,9 to account for relaxation
        initial_tension = self.Ep / self.Ec * (
                - P / sectionHomo[0] - (P * self.e ** 2 + M * self.e) / sectionHomo[2])
        initial_tension = abs(initial_tension)

        if initial_tension >= .6 * self.fpk:
            relaxation = .015
        elif initial_tension >= 0.7 * self.fpk:
            relaxation = .025
        elif initial_tension >= .8 * self.fpk:
            relaxation = .045

        sigma_pr = initial_tension * (1 - 3 * relaxation)
        sigma_cQp = initial_tension / self.Ep

        numerator = Ap * eps_cs * self.Ep + .8 * abs(initial_tension - sigma_pr) + self.Ep / self.Ec * phi * sigma_cQp
        denominator = 1 + self.Ep * Ap / (self.Ec * self.Ab) * (1 + self.Ab / self.I * sectionHomo[1] ** 2) * (
                1 + .8 * phi)

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

    # def checkInstDeflect(self, Ap, EqLoad):  # checking max isostatic deflection
    #     sectionHomo = self.sectionHomo(Ap, self.h / 2 + self.e)
    #     deflection = 5 / 384 * (self.frec_full_load - EqLoad) * self.l ** 3 / (self.Ec * sectionHomo[2])
    #
    #     if deflection < self.l / 400:
    #         return True, deflection  # a true value stands for a correct deflection
    #     else:
    #         return False, deflection  # a false value stands for an incorrect deflection

    def checkELU(self, Ap, As1=0, As2=0):

        prevAs1 = As1  # this variables will only be used if M_front < Mu
        prevAs2 = As2

        x = 1.5 * (Ap * self.fpk + As1 * self.fyk - As2 * self.fyk) / (
                1.15 * .8 * self.b * self.fck)  # check where the neutral fibre is countting on the existing Ap
        M_front = Ap * self.fpk / 1.15 * self.dp + As1 * self.fyk / 1.15 * (self.h - self.recp) \
                  - As2 * self.fyk * self.recp - 0.32 * x ** 2 * self.b * self.fck / 1.5
        # Moment generated by the current reinforcement after yielding

        if M_front < self.Mu:  # check if ELU moment is bigger than the beam´s strenght

            while self.Mu - M_front > 10:

                increAs1 = (self.Mu - M_front) * 1.15 / (
                        (self.h - self.recp) * self.fyk)  # passive reinforcement necessary
                prevAs1 += increAs1
                x = 1.5 * (Ap * self.fpk + prevAs1 * self.fyk - prevAs2 * self.fyk) / (
                        1.15 * .8 * self.b * self.fck)  # recalculate neutral fibre.

                if x / self.dp > 0.335:  # postensioned strain needs to be checked.
                    increAs2 = increAs1  # increment in top reinforecemnt is equal to the difference between
                    # the current As1 and the previus value for As1.
                    prevAs2 += increAs2

                M_front = Ap * self.fpk / 1.15 * self.dp + prevAs1 * self.fyk / 1.15 * (
                            self.h - self.recp) - prevAs2 * self.fyk * self.recp - 0.32 * x ** 2 * self.b * self.fck / 1.5

        return M_front, prevAs2, prevAs2


class reinforcedIsoBeam:
    fck = 35
    fctm = 3.2
    Ec = 34000
    Phi = 2  # creep coeffitient
    eps_cd0 = 0.00041  # initial shrinkage strain
    rec = 30  # concrete cover
    #  Passive steel properties
    fyk = 500
    Es = 200000
    # load at transfer N/mm2
    construction = 1
    # full loads N/mm
    selfweight = 0
    partwalls = 1
    use_load = 0
    # bars D:area
    bars = {
        6: 28.27,
        8: 50.27,
        10: 78.54,
        12: 113.10,
        14: 153.94,
        16: 201.06,
        20: 314.16,
        25: 490.87,
        32: 804.25,
        40: 1256.64
    }

    def __init__(self, h, b, l):
        self.h = h
        self.b = b
        self.l = l

        self.ds1 = self.h + self.rec

        self.Ab = self.h * self.b  # gross cross section
        self.Wb = self.h ** 2 * self.b / 6  # gross section modulus
        self.Wu = self.b * (self.h - self.rec) ** 2
        self.I = self.b * self.h ** 3 / 12  # gross moment of inertia
        self.selfweight = self.Ab * 24 * 1e-6

        if self.l >= 7000:
            self.use_load = 5
        else:
            self.use_load = 2

        self.charac_load = 1.35 * (self.selfweight + self.partwalls) + 1.5 * self.use_load
        self.almostper_load = self.selfweight + self.partwalls + 0.6 * self.use_load
        self.Me = self.almostper_load * self.l ** 2 / 8  # Max moment under almost permanent loads
        self.Mu = self.charac_load * self.l ** 2 / 8  # Max moment under characteristic load.

    def properties(self):
        pass

    def Wmin(self, b=0):  # in this context W means bd^2

        Wmin = self.Mu * 1.5 / (0.8 * 0.86 * 0.35 * self.fck)  # x/d is assumed to be = 0.35

        if b != 0:  # checks if a "b" parameter has been introduced
            dmin = math.sqrt(Wmin / b)
            return Wmin, dmin

        return Wmin

    def As(self):

        As = 1.15 * 0.8 * 0.35 * self.ds1 * self.b * self.fck / 1.5


if __name__ == "__main__":
    viga = posTensionedIsoBeam(5000)
    Pmin = viga.Pmin()
    Ap = viga.Ap(viga.Pmin())
    As1 = viga.checkELU(Ap)[1]
    As2 = viga.checkELU(Ap)[2]
    print(viga.cracked(Pmin, Ap, As1, As2))
    # print(viga.hflex())
    # print(viga.Iflex())
    # print(viga.timedepLosses(Pmin, Ap))
