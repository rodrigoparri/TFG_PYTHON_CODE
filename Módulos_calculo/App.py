import Beams

class IsoBeamApp:

    """
    this class contains all the logic necessary to make the app run
    """
    lengths_list = (
        5000,
        6000,
        7000,
        9000,
        8000,
        10000,
        11000,
        12000,
        13000,
        14000,
        15000
    )

    def __init__(self):
        properties_dict = {}
        self.instances={}
        # create one instance for every length in length_list
        for length in self.lengths_list:
            """
            instances is a dictionary where __str__ methods are keys and instances are values. Properties is a dictionary
            where __str__ methods are keys and each instance´s properties methods are values. 
            """
            self.instances[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length)
        #     properties_dict[str(Beams.posTensionedIsoBeam(length))] = Beams.posTensionedIsoBeam(length).Properties()
        # print(instances)
        # print(properties_dict)

    def calculations(self):



        pass


if __name__ == "__main__":
    App = IsoBeamApp()