import pandas as pd
def load_avonet(file_path):
    data = pd.read_excel(file_path)
    data
    return data

def load_birdbase(file_path):
    pass

def load_avilist(file_path):
    columns = [
        'ORDER',
        'FAMILY',
        'SCIENTIFIC NAME',
        'ENGLISH NAME: AVILIST',
        'LIST CATEGORY',
        'BIRDLIFE DATAZONE URL',
        'AVIBASE ID',
    ]

    data = pd.read_excel(file_path)
    return data.loc[data['RANK'].eq('species'), columns].copy()

LOADER_REGISTRY = {
    'AVONET': load_avonet,
    'BIRDBASE': load_birdbase,
    'AVILIST': load_avilist

}

class Dataset:
    def __init__(self, name_database, file_path):
        self.name_database = name_database
        self.file_path = file_path
        self.raw_data = None
        self.extracted_data = None
        self.loader = self.select_loader()


    def select_loader(self):
        try:
            loader = LOADER_REGISTRY[self.name_database.upper()]
        except KeyError:
            raise ValueError(
                f"No loader registered for {self.name_database}"
            )

        return loader

    def load_data(self):
        return self.loader(self.file_path)
        pass

avonet = Dataset(
    name_database='avonet',
    file_path='data/raw/AVONET Supplementary dataset 1.xlsx'
)

data = avonet.load_data()
print(avonet.loader)

birdbase = Dataset(
    name_database='birdbase',
    file_path='data/raw/BIRDBASE v2025.1 Sekercioglu et al. Final.xlsx'
)

print(birdbase.loader)

