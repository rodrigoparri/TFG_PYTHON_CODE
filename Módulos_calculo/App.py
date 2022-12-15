import Beams
import pandas as pd

class IsopostBeamApp:

    """
    this class contains all the logic necessary to make the app run
    """
    # lengths_list = list(range(5000, 15000, 500))

    def __init__(self, limit, step):
        self.PBeams = {}  # create one instance for every length in lengen
        for length in self.lengen(limit, step):
            """
            instances is a dictionary where __str__ methods are keys and instances are values. Properties is a dictionary
            where __str__ methods are keys and each instance´s properties methods are values. 
            """
            self.PBeams[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length)

    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step

    def Pcal(self):  # Calculations for postensioned beams

        # Create only one dict with each instance as key and a tuple with every result from calculations.
        # the order in the tuple will be: Pmin, Pmax, Ap, sectionHomo(tuple), instantlosses, timedeplosses, passive reinforcement, cracked.
        beamcalc = dict()
        columnnames = ()

        for instance in self.PBeams:

            b = self.PBeams[instance].b
            h = self.PBeams[instance].h
            e = self.PBeams[instance].e
            Pmin = self.PBeams[instance].Pmin()
            Pmax = self.PBeams[instance].Pmax()
            Ap = self.PBeams[instance].Ap(Pmin)
            sectionhomo = self.PBeams[instance].sectionHomo(Ap)
            instantlosses = self.PBeams[instance].instantLosses(Pmin, Ap)
            relinstlosses = instantlosses / Pmin * 100
            timedeplosses = self.PBeams[instance].timedepLosses(Pmin, Ap, sectionhomo[0], sectionhomo[1], sectionhomo[2])
            reltimedeplosses = timedeplosses / Pmin * 100
            passivereinforcement = self.PBeams[instance].checkELU(Ap)

            beamcalc[instance] = (b, h, e, Pmin, Pmax, Ap, instantlosses, relinstlosses, timedeplosses, reltimedeplosses, passivereinforcement)
            columnnames = ("b (mm)","h (mm)", "e (mm)", "Pmin (N)", "Pmax (N)", "Ap (mm2)", "instant losses (N)","relative instant losses (%)",
                           "time dependent losses (N)","relative timen dependent losses (%)", "passive reinforcement (N)")

        df = pd.DataFrame.from_dict(beamcalc, orient="index", columns=columnnames)
        pd.set_option("display.max_columns", len(columnnames))
        print(df)

class IsoreinforcedBeam:

    def __init__(self, limit, step):
        self.RBeams = {}
        for length in self.lengen(limit, step):
            pass
    @staticmethod
    def lengen(limit, step):  # method that generates the next length as it´s called

        n = 5000
        while n <= limit:
            yield n
            n += step


if __name__ == "__main__":
    App = IsopostBeamApp(20000, 500)
    App.Pcal()