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
            costs = self.IsoPBeams[instance].cost(Ap, As1, As2)

            beamcalc[instance] = (
                b,
                h,
                e,
                Pmin,
                Pmax,
                Ap,
                instantlosses,
                relinstlosses,
                timedeplosses,
                reltimedeplosses,
                As1,
                As2,
                CEcracked,
                CEdeflect,
                costs
            )

        columnnames = (
            "b (mm)",
            "h (mm)",
            "e (mm)",
            "Pmin (N)",
            "Pmax (N)",
            "Ap (mm2)",
            "instant losses (N)",
            " (%)",
            "time dependent losses (N)",
            " (%)",
            "As1 (mm2)",
            "As2 (mm2)",
            "CEcracked",
            "CEdeflection",
            "€"
        )

        pdf = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(pdf)

class IsoreinforcedBeamApp:

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
            costs = self.IsoRBeams[instance].cost(As[0], As[1])

            beamcalc[instance] = (
                b,
                h,
                Me,
                Mu,
                As[0],
                As[1],
                CEcracked,
                CEdeflect,
                costs
            )

        columnnames = (
            "b (mm)",
            "h (mm)",
            "Me (mkN)",
            "Mu (mkN)",
            "As1 (mm2)",
            "As2 (mm2)",
            "CEcracked",
            "CEdeflection",
            "€"
        )
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
            As1_neg = NegReinf[0]
            As2_neg = NegReinf[1]
            CEcracked = self.HiperPBeams[instance].CEcrack(Ap, As1_pos)
            Ptotal = Pmin + instantlosses + timedeplosses
            CEdeflect = self.HiperPBeams[instance].CEdeflect(Ptotal, Ap, As1_pos, As1_neg, sectHomo[2])
            costs = self.HiperPBeams[instance].cost(Ap, As1_pos + As2_neg , As1_neg + As2_pos)

            beamcalc[instance] = (b,
                                  h,
                                  e,
                                  Pmin,
                                  Pmax,
                                  Ap,
                                  instantlosses,
                                  relinstlosses,
                                  timedeplosses,
                                  reltimedeplosses,
                                  As1_pos,
                                  As2_pos,
                                  As1_neg,
                                  As2_neg,
                                  CEcracked,
                                  CEdeflect,
                                  costs
                                  )

        columnnames = ("b (mm)",
                       "h (mm)",
                       "e (mm)",
                       "Pmin (N)",
                       "Pmax (N)",
                       "Ap (mm2)",
                       "instant losses (N)",
                       " (%)",
                       "time dependent losses (N)",
                       " (%)", "As1_pos (mm2)",
                       "As2_pos (mm2)",
                       "As1_neg (mm2)",
                       "As2_neg (mm2)",
                       "CEcracked",
                       "Cedeflect",
                       "€"
                       )

        pdf = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(pdf)

class HiperreinforecedBeamApp:

    def __init__(self, limit, step):

        self.HiperRBeams = {}

        for length in self.lengen(limit, step):

            self.HiperRBeams[str(Beams.reinforcedHiperBeam(length))] = Beams.reinforcedHiperBeam(length)

    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step

    def HiperRcal(self):
        beamcalc = {}

        for instance in self.HiperRBeams:

            b = self.HiperRBeams[instance].b
            h = self.HiperRBeams[instance].h
            # Me = self.HiperRBeams[instance].Me * 1e-6
            # Mu = self.HiperRBeams[instance].Mu * 1e-6
            As_pos = self.HiperRBeams[instance].As_pos()
            As_neg = self.HiperRBeams[instance].As_neg()
            secthomo = self.HiperRBeams[instance].sectionHomo(As_pos[0], As_pos[1])
            CEcracked_pos = self.HiperRBeams[instance].CEcrack_pos(As_pos[0])
            CEcracked_neg = self.HiperRBeams[instance].CEcrack_neg(As_neg[0])
            CEdeflect = self.HiperRBeams[instance].CEdeflect(As_pos[0], As_pos[1],secthomo[2])
            costs = self.HiperRBeams[instance].cost(As_pos[0]+As_neg[1], As_pos[1]+As_neg[0])

            beamcalc[instance] = (
                b,
                h,
                # Me,
                # Mu,
                As_pos[0],
                As_pos[1],
                As_neg[0],
                As_neg[1],
                CEcracked_pos,
                CEcracked_neg,
                CEdeflect,
                costs
            )

        columnnames = (
            "b (mm)",
            "h (mm)",
            # "Me (mkN)",
            # "Mu (mkN)",
            "As1_pos (mm2)",
            "As2_pos (mm2)",
            "As1_neg (mm2)",
            "As2_neg (mm2)",
            "CEcracked_pos",
            "CEcracked_neg",
            "CEdeflection",
            "€"
        )
        rdf = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(rdf)

class PostensionedSlabApp:

    def __init__(self, limit, step):
        self.PSlabs = {}

        for length in self.lengen(limit, step):
            self.PSlabs[str(Beams.posTensionedSlab(length))] = Beams.posTensionedSlab(length)

    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step

    def SlabPcal(self):

        slabcalc = {}

        for instance in self.PSlabs:

            b = self.PSlabs[instance].b
            h = self. PSlabs[instance].h
            e = self. PSlabs[instance].e
            Pmin = self.PSlabs[instance].Pmin()

            if Pmin < 0:
                Pmin = self.PSlabs[instance].Pequiv(self.PSlabs[instance].selfweight * b / 8)

            Pmax = self.PSlabs[instance].Pmax()
            Ap = self.PSlabs[instance].Ap(Pmin)
            Sh = self.PSlabs[instance].sectionHomo(Ap)
            instLosses = self.PSlabs[instance].instantLosses(Pmin, Ap)
            relinstLosses = instLosses / Pmin * 100
            timedepLosses = self.PSlabs[instance].timedepLosses(Pmin, Ap, Sh[0], Sh[1], Sh[2])
            reltimedepLosses = timedepLosses / Pmin * 100
            posReinf = self.PSlabs[instance].checkELUpos(Ap)
            negReinf = self.PSlabs[instance].checkELUneg(Ap)
            As1_pos = posReinf[0]
            As2_pos = posReinf[1]
            As1_neg = negReinf[0]
            As2_neg = negReinf[1]
            CEcracked = self.PSlabs[instance].CEcrack(Ap, As1_pos)
            Ptotal = Pmin + instLosses + timedepLosses
            CEdeflect = self.PSlabs[instance].CEdeflect(Ptotal, Ap, As1_pos, As1_neg, Sh[2])
            costs = self.PSlabs[instance].cost(Ap, As1_pos + As2_neg, As2_pos + As1_neg)

            slabcalc[instance] = (b,
                                  h,
                                  e,
                                  Pmin,
                                  Pmax,
                                  Ap,
                                  instLosses,
                                  relinstLosses,
                                  timedepLosses,
                                  reltimedepLosses,
                                  As1_pos,
                                  As2_pos,
                                  As1_neg,
                                  As2_neg,
                                  CEcracked,
                                  CEdeflect,
                                  costs
                                  )

        columnnames = (
            "b (mm)",
            "h (mm)",
            "e (mm)",
            "Pmin (N)",
            "Pmax (N)",
            "Ap (mm2)",
            "instant losses (N)",
            " (%)",
            "time dependent losses (N)",
            " (%)", "As1_pos (mm2)",
            "As2_pos (mm2)",
            "As1_neg (mm2)",
            "As2_neg (mm2)",
            "CEcracked",
            "Cedeflect",
            "€"
           )

        pdf = pd.DataFrame.from_dict(slabcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(pdf)

class ReinforcedSlabApp:

    def __init__(self, limit, step):

        self.ReinfSlabs = {}

        for length in self.lengen(limit, step):

            self.ReinfSlabs[str(Beams.reinforcedSlab(length))] = Beams.reinforcedSlab(length)

    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step

    def SlabRcal(self):
        beamcalc = {}

        for instance in self.ReinfSlabs:

            b = self.ReinfSlabs[instance].b
            h = self.ReinfSlabs[instance].h
            # Me = self.HiperRBeams[instance].Me * 1e-6
            # Mu = self.HiperRBeams[instance].Mu * 1e-6
            As_pos = self.ReinfSlabs[instance].As_pos()
            As_neg = self.ReinfSlabs[instance].As_neg()
            secthomo = self.ReinfSlabs[instance].sectionHomo(As_pos[0], As_pos[1])
            As_min = self.ReinfSlabs[instance].As_min(secthomo[1])

            pos = False
            neg = False
            if As_pos[0] < As_min:
                CEcracked_pos = self.ReinfSlabs[instance].CEcrack_pos(As_min)
                # As_pos = As_min
                pos = True
            else:
                CEcracked_pos = self.ReinfSlabs[instance].CEcrack_pos(As_pos[0])

            if As_neg[0] < As_min:
                CEcracked_neg = self.ReinfSlabs[instance].CEcrack_neg(As_min)
                # As_neg = As_min
                neg = True
            else:
                CEcracked_neg = self.ReinfSlabs[instance].CEcrack_neg(As_neg[0])

            costs = self.ReinfSlabs[instance].cost(As_pos[0]+As_neg[1], As_pos[1]+As_neg[0])
            # if pos == True and neg == True:
            #     CEdeflect = self.ReinfSlabs[instance].CEdeflect(As_min, As_min, secthomo[2])
            # elif pos == True and neg == False:
            #     CEdeflect = self.ReinfSlabs[instance].CEdeflect(As_min, As_neg[0], secthomo[2])
            # elif pos == False and neg == True:
            #     CEdeflect = self.ReinfSlabs[instance].CEdeflect(As_pos[0], As_min, secthomo[2])
            # else:
            #     CEdeflect = self.ReinfSlabs[instance].CEdeflect(As_pos[0], As_neg[0], secthomo[2])

            CEdeflect = self.ReinfSlabs[instance].CEdeflect(As_pos[0], As_neg[0], secthomo[2])

            beamcalc[instance] = (
                b,
                h,
                # Me,
                # Mu,
                As_pos[0],
                As_pos[1],
                As_neg[0],
                As_neg[1],
                CEcracked_pos,
                CEcracked_neg,
                CEdeflect,
                costs
            )

        columnnames = (
            "b (mm)",
            "h (mm)",
            # "Me (mkN)",
            # "Mu (mkN)",
            "As1_pos (mm2)",
            "As2_pos (mm2)",
            "As1_neg (mm2)",
            "As2_neg (mm2)",
            "CEcracked_pos",
            "CEcracked_neg",
            "CEdeflection",
            "€"
        )

        rdf = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(rdf)


if __name__ == "__main__":

    # App = IsopostBeamApp(25000, 500)
    # App.IsoPcal()

    # App2 = IsoreinforcedBeamApp(25000, 500)
    # App2.IsoRcal()

    # App3 = HiperpostBeamApp(25000, 500)
    # App3.HiperPcal()

    # App4 = HiperreinforecedBeamApp(25000, 500)
    # App4.HiperRcal()

    App5 = PostensionedSlabApp(25000, 500)
    App5.SlabPcal()

    App6 = ReinforcedSlabApp(25000, 500)
    App6.SlabRcal()