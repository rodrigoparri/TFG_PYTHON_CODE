

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
        instances=[]
        # create one instance for every length in length_list
        for length in self.lengths_list:


