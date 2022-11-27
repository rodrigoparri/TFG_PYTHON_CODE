import Beams

class IsoBeamApp:

    """
    this class contains all the logic necessary to make the app run
    """
    lengths_list = (
        5000,
        6000,
        7000,
        8000,
        9000,
        10000,
        11000,
        12000,
        13000,
        14000,
        15000
    )

    def __init__(self):
        properties_dict = {}
        self.PBeams={}
        # create one instance for every length in length_list
        for length in self.lengths_list:
            """
            instances is a dictionary where __str__ methods are keys and instances are values. Properties is a dictionary
            where __str__ methods are keys and each instance´s properties methods are values. 
            """
            self.PBeams[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length)
        #     properties_dict[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length).Properties()
        # print(instances)
        # print(properties_dict)

    def Pcal(self):  # Calculations for postensioned beams

        # Create dictionaries with the instance´s properties necessary for the calculations
        Pmin_dict = {}
        Pmax_dict = {}
        Ap_dict = {}
        InstantLosses_dict = {}
        TimedepLosses_dict = {}
        PasiveReinforcement_dict = {}


        for instance in self.PBeams:

            Pmin_dict[instance] = self.PBeams[instance].Pmin()
            Pmax_dict[instance] = self.PBeams[instance].Pmax()
            Ap_dict[instance] = self.PBeams[instance].Ap(Pmin_dict[instance])
            InstantLosses_dict[instance] = self.PBeams[instance].instantLosses(Pmin_dict[instance], Ap_dict[instance])
            TimedepLosses_dict[instance] = self.PBeams[instance].timedepLosses(Pmin_dict[instance], Ap_dict[instance])

        print(Pmin_dict)
        print(Pmax_dict)
        print(Ap_dict)
        print(InstantLosses_dict)
        print(TimedepLosses_dict)

        for instance in self.PBeams:

            PasiveReinforcement_dict[instance] = self.PBeams[instance].checkELU(Ap_dict[instance])[1], \
                                                 self.PBeams[instance].checkELU(Ap_dict[instance])[2]

        print(PasiveReinforcement_dict)
if __name__ == "__main__":
    App = IsoBeamApp()
    App.Pcal()