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
    reca = 40  # concrete cover of the active reinforcement
    # Active steel properties
    fpk = 1860
    # fpd = 1617.391
    fbpt = 4.8
    Ep = 195000
    #  Passive steel properties
    fyk = 500
    Es = 200000
    recp = 30  # passive reinforcement concrete cover
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
    # tendoms
    tendoms = {
        12.7: 98.74,
        15.2: 140
    }

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
        self.ds1 = self.h + self.recp

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
        homosection = self.sectionHomo(Ap)
        instantLosses = self.instantLosses(Pmin, Ap)
        timedepLosses = self.timedepLosses(Pmin, Ap,homosection[0], homosection[1], homosection[2])

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
                "Mf mKN": self.Mf * 1e-6,
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
        :param div: is the distance between those discrete values
        :return: the value within the set just above it
        """
        a = int(value / div) * div
        a += div
        return a

    def hflex(self):  # COMPROBAR QUE LA SALIDA DE HFLEX ES IGUAL A LAS H Y B ELEGIDAS SI SON MAYORES PONER LAS DE HFLEX.
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
        Ah = self.b * self.h + (np - 1) * Ap + (ns - 1) * (As1 + As2)  # homogeneous cross section
        # position of the centroid from top fibre
        y = (self.h / 2 * (self.h * self.b) + self.dp * (ns - 1) * Ap + d1 * (ns - 1) * As1 + d2 * (ns - 1) * As2) / Ah
        Ih = self.b * self.h ** 3 / 12 + Ap * (np - 1) * self.dp ** 2 + d1 ** 2 * (ns - 1) * As1 + d2 ** 2 * (
                    ns - 1) * As2
        return Ah, y, Ih  # Homogenized cross section, neutral plane, depth homogenized inertia.


    def CEcrack(self, P, Ap, As1, As2):
        phi = 0
        m = 0
        for bar in self.bars:
            m = As1 / self.bars[bar]
            m = self.aprox(m, 1)

            if (2 * self.recp + m * bar + (m - 1) * 20) > self.b:
                continue
            else:
                phi = bar
                break

        phi_p = 0
        Ap_list = []
        for tendom in self.tendoms:
            t = Ap / self.tendoms[tendom]
            t = self.aprox(t, 1)
            a = (t * self.tendoms[tendom] - Ap)
            Ap_list.append(a)

        if Ap_list[0] <= Ap_list[1]:
            phi_p = 12.7
        elif Ap_list[0] > Ap_list[1]:
            phi_p = 15.2

        Xi_1 = math.sqrt(0.5 * phi / phi_p)
        h_Cr = min(2.5 * self.reca, self.h / 2, (0.65 * self.h + 0.35 * self.reca) / 3)
        A_ceff = self.b * h_Cr
        rho_peff = (As1 + Xi_1 * Ap) / A_ceff
        s_r = 3.4 * self.reca + 1.6 * 0.5 * 0.425 * phi / rho_peff

        eps_c = -1 * 0.6 * self.fck / self.Ec
        # eps_p1 = P / (self.Ep * Ap)
        # eps_p2 = 1 / self.Ec * (P / self.Ab + P * self.e ** 2 / self.I)
        eps_p3 = -eps_c * (self.dp / (self.h - h_Cr) - 1)
        sigma_s = self.Ep * eps_p3

        alpha_e = self.Ep / self.Ec
        diff_eps = (sigma_s - 0.4 * self.fctm / rho_peff * (1 + alpha_e * rho_peff)) / self.Es
        lim = 0.6 * sigma_s / self.Es

        if diff_eps < lim:
            diff_eps = lim

        w_k = s_r * diff_eps

        if w_k < 0.2:
            return "OK"
        else:
            return "NOT OK"

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

    def timedepLosses(self, P, Ap, areahomo, depthhomo, inertiahomo):

        M = self.Me
        phi = 2
        ho = self.Ab / (self.h + self.b)
        kh = 0
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
                - P / areahomo - (P * self.e ** 2 + M * self.e) / inertiahomo)
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
        denominator = 1 + self.Ep * Ap / (self.Ec * self.Ab) * (1 + self.Ab / self.I * depthhomo ** 2) * (
                1 + .8 * phi)

        timedepLosses = numerator / denominator
        return timedepLosses

    def Ap(self, P):
        Apin = 10  # trialAp must always be bigger than the reference value in the while loop
        Apout = 0

        while True:  # reference value.
            Apout = self.instantLosses(P, Apin) / (0.1 * self.fpk)
            if abs(Apout - Apin) > 1:
                Apin = Apout
                continue
            else:
                break
        return Apout


    def checkELU(self, Ap, As1=0, As2=0):

        prevAs1 = As1  # this variables will only be used if M_front < Mu
        prevAs2 = As2

        x = 1.5 * (Ap * self.fpk + As1 * self.fyk - As2 * self.fyk) / (
                1.15 * .8 * self.b * self.fck)  # check where the neutral fibre is countting on the existing Ap
        M_front = Ap * self.fpk / 1.15 * self.dp + As1 * self.fyk / 1.15 * (self.h - self.recp) \
                  - As2 * self.fyk * self.recp - 0.32 * x ** 2 * self.b * self.fck / 1.5
        # Moment generated by the current reinforcement after yielding

        if M_front < self.Mu:  # check if ELU moment is bigger than the beam´s strenght

            while self.Mu - M_front > 0:

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
                            self.h - self.recp) - prevAs2 * self.fyk * self.recp / 1.15 - 0.32 * x ** 2 * self.b * self.fck / 1.5

        return prevAs1, prevAs2


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
    flooring = 1.5
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
    length_fraction = 19

    def __init__(self, l):

        height = l / self.length_fraction  # first h aproximation
        haprox = int(height / 50) * 50
        if haprox < height:
            height = haprox + 50
        else:
            height = haprox

        width = int(height * 2 / 150) * 50
        if width < (height * 2 / 3):
            self.b = width + 50
        else:
            self.b = width

        self.l = l

        self.Ab = height * self.b  # gross cross section
        self.Wb = height ** 2 * self.b / 6  # gross section modulus
        self.Wu = self.b * (height - self.rec) ** 2
        self.I = self.b * height ** 3 / 12  # gross moment of inertia
        self.selfweight = self.Ab * 24 * 1e-6

        if self.l >= 7000:
            self.use_load = 5
        else:
            self.use_load = 2

        self.charac_load = 1.35 * (self.selfweight + self.partwalls + self.flooring) + 1.5 * self.use_load
        self.almostper_load = self.selfweight + self.partwalls + self.flooring + 0.6 * self.use_load
        self.Me = self.almostper_load * self.l ** 2 / 8  # Max moment under almost permanent loads
        self.Mu = self.charac_load * self.l ** 2 / 8  # Max moment under characteristic load.

        hmin = self.Wmin(self.b)[1] + self.rec

        if height < hmin:

            self.h = self.aprox(height,50)
        else:
            self.h = height

        self.ds1 = self.h - self.rec

    def __str__(self) -> str:
        text = f"IsoRB{self.l / 1000}"
        return text

    @staticmethod
    def aprox(value, div):
        """
        aproximate any continuous value to a set of discrete equally spaced values.
        :param value: value is the value you want to aproximate to an infinite set of discrete equally spaced values
        :param div: is the distance between those discrete values
        :return: the value within the set just above it
        """
        a = int(value / div) * div
        a += div
        return a

    def properties(self):

        As = self.As()
        Wmin = self.Wmin(self.b)[0]
        dmin = self.Wmin(self.b)[1]
        CEcrack = self.CEcrack(As[0], As[1])

        return {
            "h mm": self.h,
            "b mm": self.b,
            "Wb cm3":self.Wb,
            "Wmin cm3":Wmin,
            "dmin mm":dmin,
            "Ib cm4": self.I,
            "self weight kN/m": self.selfweight,
            "char load kN/m": self.charac_load,
            "almost frecuent load": self.almostper_load,
            "Me mkN": self.Me,
            "Mu mKN":self.Mu,
            "As1 mm2": As[0],
            "As2 mm2": As[1],
            "Cracked": CEcrack
                }

    def Wmin(self, b=0):  # in this context W means bd^2

        Wmin = self.Mu * 1.5 / (0.8 * 0.86 * 0.35 * self.fck)  # x/d is assumed to be = 0.35

        if b != 0:  # checks if a "b" parameter has been introduced
            dmin = math.sqrt(Wmin / b)
            return Wmin, dmin
        else:
            return Wmin

    def As(self):
        x = 0
        M = 0.8 * x * self.fck * self.b * (self.ds1 - 0.8 * x / 2) / 1.5
        prevAs1 = 0
        prevAs2 = 0

        while self.Mu > M:
            increAs1 = (self.Mu - M) * 1.15 / ((self.h - self.rec) * self.fyk)  # passive reinforcement necessary
            prevAs1 += increAs1
            x = 1.5 * (prevAs1 * self.fyk - prevAs2 * self.fyk) / (1.15 * .8 * self.b * self.fck)   # recalculate neutral fibre.

            if x / self.ds1 > 0.35:  # strain needs to be checked.
                increAs2 = increAs1  # increment in top reinforcement is equal to the difference between
                # the current As1 and the previous value for As1.
                prevAs2 += increAs2

            M = prevAs1 * self.fyk / 1.15 * self.ds1 - prevAs2 * self.fyk / 1.15 * self.rec - 0.32 * x ** 2 * self.b * self.fck / 1.5

        return prevAs1, prevAs2

    def sectionHomo(self, As1=0, d1=0, As2=0, d2=0):
        # As1 and As2 are the bottom and top passive reinforcement areas
        ns = self.Es / self.Ec
        Ah = self.b * self.h + (ns - 1) * (As1 + As2)  # homogeneous cross section
        # position of the centroid from top fibre
        y = (self.h / 2 * (self.h * self.b) + d1 * (ns - 1) * As1 + d2 * (ns - 1) * As2) / Ah
        Ih = self.b * self.h ** 3 / 12 + d1 ** 2 * (ns - 1) * As1 + d2 ** 2 * (
                    ns - 1) * As2
        return Ah, y, Ih  # Homogenized cross section, neutral plane, depth homogenized inertia.


    def CEcrack(self, As1, As2):
        phi = 0
        m = 0
        for bar in self.bars:
            m = As1 / self.bars[bar]
            m = self.aprox(m, 1)

            if (2 * self.rec + m * bar + (m - 1) * 20) > self.b:
                continue
            else:
                phi = bar
                break

        # Xi_1 = math.sqrt(0.5)
        h_Cr = (2.5 * self.rec, self.h / 2, (0.65 * self.h + 0.35 * self.rec) / 3)
        A_ceff = self.b * min(h_Cr)
        rho_peff = (As1)/ A_ceff
        s_r = 3.4 * self.rec + 0.8 * 0.5 * 0.425 * phi / rho_peff

        if phi == 6:
            sigma_s = 450
        elif phi == 8:
            sigma_s = 400
        elif phi == 10:
            sigma_s = 360
        elif phi == 12:
            sigma_s = 320
        elif phi == 14:
            sigma_s = 280
        elif phi == 16:
            sigma_s = 280
        elif phi == 20:
            sigma_s = 240
        elif phi == 25:
            sigma_s = 200
        elif phi == 32:
            sigma_s = 200
        else:
            sigma_s = 160

        alpha_e = self.Es / self.Ec
        diff_eps = (sigma_s - 0.4 * self.fctm / rho_peff * (1 + alpha_e * rho_peff)) / self.Es
        lim = 0.6 * sigma_s / self.Es

        if diff_eps < lim:
            diff_eps = lim

        w_k = s_r * diff_eps

        if w_k < 0.4:
            return "OK"
        else:
            return "NOT OK"

    def CEdeflect(self, As1, As2, inertiahomo):
        rho = As1 / self.Ab
        rho_ = As2 / self.Ab
        rho_0 = 1e-3 * math.sqrt(self.fck)
        a = rho_0 / rho
        b = rho_0 / (rho - rho_)
        K = 1
        ld = 0
        ld_0 = self.l / self.ds1

        if rho <= rho_0:
            ld = K * (11 + 1.5 * math.sqrt(self.fck) * a + 3.2 * math.sqrt(self.fck) * pow(a - 1, 3 / 2))
        else:
            ld = K * (11 + 1.5 * math.sqrt(self.fck) * b + 1 / 12 * math.sqrt(self.fck * rho_ / rho_0))

        if ld_0 <= ld:
            return "OKi"
        else:
            n = self.Es / self.Ec
            m = rho_ / rho
            xd = n * rho * (1 + m) * (
                -1 + math.sqrt(1 + 2 * (1 + m * self.rec / self.ds1) / (
                n * rho * (1 + m) ** 2 ))) # Cracked inertia from centroid

            x = xd * self.ds1
            I_f = n * As1 * (self.ds1 - x) * (self.ds1 - x / 3) + n * As2 * (
                x - self.rec) * (x / 3 - self.rec )

            Eceff = self.Ec / (1 + self.Phi)
            Mf = self.Wb * self.fctm
            Xi = 1 - 0.5 * (Mf / self.Me) ** 2
            ke = self.Me / (Eceff * inertiahomo)
            kf = self.Me / (Eceff * I_f)
            k = Xi * kf + (1 - Xi) * ke

            deflection = k * 5 / 48 * self.l ** 2

            if deflection < self.l / 400:
                return "OK"
            else:
                return "NOT OK"





if __name__ == "__main__":
    # viga = posTensionedIsoBeam(10000)
    # Pmin = viga.Pmin()
    # Ap = viga.Ap(Pmin)
    # As = viga.checkELU(Ap)
    # Sh = viga.sectionHomo(Ap,As[0], As[1])
    # Instantalosses = viga.instantLosses(Pmin, Ap)
    # Timedeplosses = viga.timedepLosses(Pmin, Ap, Sh[0], Sh[1], Sh[2])
    # print(viga.CEcrack(Pmin + Instantalosses + Timedeplosses, Ap,As[0], As[1]))
    # print(viga.cracked(Pmin + Instantalosses + Timedeplosses, Ap))

    """
    Podríamos asumir que habiendo cumplido el equilibrio de momentos no hace falta cumplir el equilibrio de fuerzas 
    """
    viga2 = reinforcedIsoBeam(10000)
    As = viga2.As()
    # print(As)
    # # print(viga2.h)
    # # print(viga2.cracked(As[0],As[1]))
    sectionhomo = viga2.sectionHomo(As[0], As[1])
    print(viga2.CEdeflect(As[0], As[1], sectionhomo[2]))
