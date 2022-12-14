import Beams
import pandas as pd

class IsoBeamApp:

    """
    this class contains all the logic necessary to make the app run
    """
    # lengths_list = list(range(5000, 15000, 500))

    def __init__(self, limit, step):
        properties_dict = {}
        self.PBeams={}
        # create one instance for every length in length_list
        for length in self.lengen(limit, step):
            """
            instances is a dictionary where __str__ methods are keys and instances are values. Properties is a dictionary
            where __str__ methods are keys and each instance´s properties methods are values. 
            """
            self.PBeams[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length)
        #     properties_dict[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length).Properties()
        # print(instances)
        # print(properties_dict)

    @staticmethod
    def lengen(limit, step):

        n = 5000
        while n < limit:
            yield n
            n += step

    def Pcal(self):  # Calculations for postensioned beams

        # Create dictionaries with the instance´s properties necessary for the calculations
        Pmin_dict = {}
        Pmax_dict = {}
        Ap_dict = {}
        InstantLosses_dict = {}
        TimedepLosses_dict = {}
        PasiveReinforcement_dict = {}
        dict_1 = self.PBeams

        for instance in self.PBeams:

            Pmin_dict[instance] = self.PBeams[instance].Pmin()
            Pmax_dict[instance] = self.PBeams[instance].Pmax()
            Ap_dict[instance] = self.PBeams[instance].Ap(Pmin_dict[instance])
            InstantLosses_dict[instance] = self.PBeams[instance].instantLosses(Pmin_dict[instance], Ap_dict[instance])
            TimedepLosses_dict[instance] = self.PBeams[instance].timedepLosses(Pmin_dict[instance], Ap_dict[instance])

        df = pd.DataFrame.from_dict([])
        print(f"Pmin {Pmin_dict}")
        print(f"Pmax {Pmax_dict}")
        print(f"Ap {Ap_dict}")
        print(f"InstantLosses {InstantLosses_dict}")
        print(f"TimedepLosses {TimedepLosses_dict}")

        for instance in self.PBeams:

            PasiveReinforcement_dict[instance] = self.PBeams[instance].checkELU(Ap_dict[instance])[1], \
                                                 self.PBeams[instance].checkELU(Ap_dict[instance])[2]

        print(PasiveReinforcement_dict)
        print(df)

if __name__ == "__main__":
    App = IsoBeamApp()
    App.Pcal()