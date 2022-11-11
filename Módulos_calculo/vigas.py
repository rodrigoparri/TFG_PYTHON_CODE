class posTensionedBeam:

    # concrete properties
    fck = 35000
    fckt = 24700
    fctm = 3200
    fctmt = 2400
    Ect = 31300000
    Ec = 34000000
    Ab = 0  # gross cross section
    Wb = 0  # gross section modulus
    # steel properties
    fpk = 1860000
    fpd = 1617391
    Ep = 195000000
    # load at transfer kN/m2
    construction = 1
    # full loads kN/m2
    selfweight = 0
    partwalls = 1
    use = 0
    # load combinations
    charac_load = 0
    frec_transfer_load = 0
    frec_full_load = 0
    almostper_load = 0

    def __init__(self, h, b, l, e,):

        self.h = h
        self.b = b
        self.l = l
        self. e = e

        self.Ab = self.h * self.b
        self.Wb = self.b * self.h ** 2 / 6
        self.selfweight = self.Ab * 24

        if self.l >= 7:
            self.use = 5
        else:
            self.use = 2

        self.charac_load = 1.35 * (self.selfweight + self.partwalls) + 1.5 * self.use
        self.frec_transfer_load = self.selfweight + self.construction * 0.7
        self.frec_full_load = self.selfweight + self.partwalls + 0.7 * self.use
        self.almostper_load = self.selfweight + self.partwalls + 0.6 * self.use

    def debug(self):
        print({"Ab": self.Ab,
               "Wb": self.Wb,
               "self weight": self.selfweight,
               "char load": self.charac_load,
               "frec tranfer load": self.frec_transfer_load,
               "frec full load": self.frec_full_load,
               "almost frecuent load": self.almostper_load
               })



if __name__ == "__main__":

    viga = posTensionedBeam(.2, .15, 5, 0.03)
    viga.debug()

