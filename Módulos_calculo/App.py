import Beams
import pandas as pd

class IsopostBeamApp:

    """
    this class contains all the logic necessary to make the app run
    """
    # lengths_list = list(range(5000, 15000, 500))

    def __init__(self, limit, step):
        self.IsoPBeams = {}  # create one instance for every length in lengen
        for length in self.lengen(limit, step):
            """
            instances is a dictionary where __str__ methods are keys and instances are values. Properties is a dictionary
            where __str__ methods are keys and each instance´s properties methods are values. 
            """
            self.IsoPBeams[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length)

    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step

    def IsoPcal(self):  # Calculations for postensioned beams

        # Create only one dict with each instance as key and a tuple with every result from calculations.
        # the order in the tuple will be: Pmin, Pmax, Ap, sectionHomo(tuple), instantlosses, timedeplosses, passive reinforcement, cracked.
        beamcalc = dict()

        for instance in self.IsoPBeams:

            b = self.IsoPBeams[instance].b
            h = self.IsoPBeams[instance].h
            e = self.IsoPBeams[instance].e
            Pmin = self.IsoPBeams[instance].Pmin()
            Pmax = self.IsoPBeams[instance].Pmax()
            Ap = self.IsoPBeams[instance].Ap(Pmin)
            sectionhomo = self.IsoPBeams[instance].sectionHomo(Ap)
            instantlosses = self.IsoPBeams[instance].instantLosses(Pmin, Ap)
            relinstlosses = instantlosses / Pmin * 100
            timedeplosses = self.IsoPBeams[instance].timedepLosses(Pmin, Ap, sectionhomo[0], sectionhomo[1], sectionhomo[2])
            reltimedeplosses = timedeplosses / Pmin * 100
            passivereinforcement = self.IsoPBeams[instance].checkELU(Ap)
            As1 = passivereinforcement[0]
            As2 = passivereinforcement[1]
            CEcracked = self.IsoPBeams[instance].CEcrack(Pmin, Ap, passivereinforcement[0], passivereinforcement[1])
            CEdeflect = self.IsoPBeams[instance].CEdeflect(Pmin, Ap, As1, As2, sectionhomo[2])

            beamcalc[instance] = (b, h, e, Pmin, Pmax, Ap, instantlosses, relinstlosses, timedeplosses, reltimedeplosses,
                                  As1, As2, CEcracked, CEdeflect)

        columnnames = ("b (mm)","h (mm)", "e (mm)", "Pmin (N)", "Pmax (N)", "Ap (mm2)", "instant losses (N)"," (%)",
                           "time dependent losses (N)"," (%)", "As1 (mm2)", "As2 (mm2)", "CEcracked", "CEdeflection")

        pdf = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(pdf)

class IsoreinforcedBeam:

    def __init__(self, limit, step):

        self.IsoRBeams = {}

        for length in self.lengen(limit, step):

            self.IsoRBeams[str(Beams.reinforcedIsoBeam(length))] = Beams.reinforcedIsoBeam(length)

    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step

    def IsoRcal(self):
        beamcalc = {}

        for instance in self.IsoRBeams:

            b = self.IsoRBeams[instance].b
            h = self.IsoRBeams[instance].h
            Me = self.IsoRBeams[instance].Me * 1e-6
            Mu = self.IsoRBeams[instance].Mu * 1e-6
            As = self.IsoRBeams[instance].As()
            secthomo = self.IsoRBeams[instance].sectionHomo(As[0], As[1])
            CEcracked = self.IsoRBeams[instance].CEcrack(As[0], As[1])
            CEdeflect = self.IsoRBeams[instance].CEdeflect(As[0], As[1],secthomo[2])

            beamcalc[instance] = (b, h, Me, Mu, As[0], As[1], CEcracked, CEdeflect)

        columnnames = ("b (mm)", "h (mm)", "Me (mkN)", "Mu (mkN)", "As1 (mm2)",
                       "As2 (mm2)", "CEcracked", "CEdeflection")
        rdf = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(rdf)

class HiperpostBeamApp:

    def __init__(self, limit, step):

        self.HiperPBeams = {}

        for length in self.lengen(limit, step):
            self.HiperPBeams[str(Beams.posTensionedHiperBeam(length))] = Beams.posTensionedHiperBeam(length)

    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step

    def HiperPcal(self):
        beamcalc = {}

        for instance in self.HiperPBeams:

            b = self.HiperPBeams[instance].b
            h = self.HiperPBeams[instance].h
            e = self.HiperPBeams[instance].e
            # Me_pos = self.HiperPBeams[instance].Me_pos
            # Me_neg = self.HiperPBeams[instance].Me_neg
            # Mu_pos = self.HiperPBeams[instance].Mu_pos
            # Mu_neg = self.HiperPBeams[instance].Mu_neg
            Pmin = self.HiperPBeams[instance].Pmin()
            Pmax = self.HiperPBeams[instance].Pmax()
            Ap = self.HiperPBeams[instance].Ap(Pmin)
            sectHomo = self.HiperPBeams[instance].sectionHomo(Ap)
            instantlosses = self.HiperPBeams[instance].instantLosses(Pmin, Ap)
            relinstlosses = instantlosses / Pmin * 100
            timedeplosses = self.HiperPBeams[instance].timedepLosses(Pmin, Ap, sectHomo[0], sectHomo[1],sectHomo[2])
            reltimedeplosses = timedeplosses / Pmin * 100
            PosReinf = self.HiperPBeams[instance].checkELUpos(Ap)
            NegReinf = self.HiperPBeams[instance].checkELUneg(Ap)
            As1_pos = PosReinf[0]
            As2_pos = PosReinf[1]
            As1_neg = PosReinf[0]
            As2_neg = PosReinf[1]
            # CEcracked = self.HiperPBeams[instance].CEcrack(Pmin, Ap, PosReinf[0], PosReinf[1])
            # CEdeflect = self.HiperPBeams[instance].CEdeflect(Pmin, Ap, As1, As2, sectHomo[2])

            beamcalc[instance] = (b, h, e, Pmin, Pmax, Ap, instantlosses, relinstlosses, timedeplosses, reltimedeplosses,
                                  As1_pos, As2_pos, As1_neg, As2_neg)

        columnnames = ("b (mm)","h (mm)", "e (mm)", "Pmin (N)", "Pmax (N)", "Ap (mm2)", "instant losses (N)"," (%)",
                           "time dependent losses (N)"," (%)", "As1_pos (mm2)", "As2_pos (mm2)", "As1_neg (mm2)", "As2_neg (mm2)")

        pdf = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(pdf)

if __name__ == "__main__":
    """ 
    hay algún problema con la fisuración en ambas vigas, a mayor canto se produce mayor fisuración lo que parece
    sin sentido. 
    """

    # App = IsopostBeamApp(25000, 1000)
    # App.IsoPcal()
    #
    # App2 = IsoreinforcedBeam(25000, 1000)
    # App2.IsoRcal()

    App3 = HiperpostBeamApp(25000, 1000)
    App3.HiperPcal()