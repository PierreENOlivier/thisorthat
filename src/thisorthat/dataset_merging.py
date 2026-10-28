import pandas as pd
from pathlib import Path
from thisorthat.utils import get_project_root

ROOT = get_project_root()
print(ROOT)

# REPO_ROOT = Path(__file__)

COLUMN_MAPPINGS = {
    'AVONET': {
        'rename': {
            'Avibase.ID1': 'avibase_id',
            'Species1': 'scientific_name',
            'Beak.Length_Culmen': 'beak_length_mm',
            'Wing.Length': 'wing_length_mm',
            'Tail.Length': 'tail_length_mm',
            'Mass': 'body_mass_gr'

        },
        'transform': {
        },
        'col_keep': [
            'avibase_id',
            'scientific_name',
            'beak_length_mm',
            'wing_length_mm',
            'tail_length_mm',
            'body_mass_gr',

        ]
    },
    'BIRDBASE': {
        'rename': {
            'avibase_id': 'avibase_id'
        },
        'transform': {},
        'col_keep': [
            'avibase_id',
            'birdnet_id',
            'birdlife_id',
            'scientific_name',
            'common_name',
            'commonness',
            'image_author',
            'image_license',
            'image_source',
            'image_url'
        ],
    },
    'AVILIST': {
        'rename': {
            'ORDER': 'order',
            'FAMILY': 'family',
            'SCIENTIFIC NAME': 'scientific_name',
            'ENGLISH NAME: AVILIST': 'common_name',
            'IUCN RED LIST CATEGORY': 'red_list',
            'BIRDLIFE DATAZONE URL': 'datazone_url',
            'AVIBASE ID': 'avibase_id',
        },
        'transform': {},
        'col_keep': [
            'avibase_id',
            'order',
            'family',
            'scientific_name',
            'red_list',
            'datazone_url'
        ]

    },
}

def load_avonet(dataset):
    col_mapping = COLUMN_MAPPINGS[dataset.name_database.upper()]

    data = pd.read_excel(
        io=ROOT / dataset.file_path,
        sheet_name='AVONET1_BirdLife',
    )

    data = data.rename(columns=col_mapping['rename'])
    return data.loc[, col_mapping['col_keep']].copy()

def load_birdbase(dataset):
    col_mapping = COLUMN_MAPPINGS[dataset.name_database.upper()]

    data = pd.read_csv(
        ROOT / dataset.file_path,
        sep=',',
        header=0
    )

    data = data.rename(columns=col_mapping['rename'])
    data.dropna(subset=['image_url'], inplace=True)


    return data = data.loc[data['record_type'] == 'species'].copy()

def load_avilist(dataset):
    col_mapping = COLUMN_MAPPINGS[dataset.name_database.upper()]

    data = pd.read_excel(
        io=ROOT / dataset.file_path,
        sheet_name='AviList v2026',
    )
    data = data.rename(columns=col_mapping['rename'])
    data['avibase_id'] = data['avibase_id'].str.split('-', expand=True)[1]
    return data.loc[data['RANK'].eq('species'), col_mapping['col_keep']].copy()

LOADER_REGISTRY = {
    'AVONET': load_avonet,
    'BIRDBASE': load_birdbase,
    'AVILIST': load_avilist

}

class Dataset:
    def __init__(self, name_database, source, file_path):
        self.name_database = name_database
        self.source = source
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
        self.data_processed = self.loader(self)
        return self.data_processed

    def consolidate_taxonomy(self, avilist):
        data_table = self.data_processed.copy()
        data_avilist = avilist.data_processed.copy()

        # pd.merge

class ConsolidatedDataset:
    def __init__(
            self,
            merged_dataset,
            source_datasets=None
    ):
        self.merged_dataset = merged_dataset
        self.source_datasets = source_datasets or []

    @classmethod
    def merge_datasets(
            cls,
            ref_dataset,
            other_sources,
            on,
            how="outer"
    ):
        if not ref_dataset:
            raise ValueError("The reference dataset 'ref_dataset' is required!")

        if not other_sources:
            raise ValueError("At least one other dataset needs to be provided for merging with 'ref_dataset'.")

        for dataset in [ref_dataset] + other_sources:
            if not isinstance(dataset, Dataset):
                raise TypeError(
                    "All datasets must be Dataset instances; "
                    f"instead got {type(dataset).__name__}"
                )

def complete_dataset(dataset):
    """
    Keep only observations that have complete
    :return:
    """
    # Should it be a function or a method?
    # Functions need to filter by tag, maybe add a tag to object and add it as a column
    pass

avilist = Dataset(
    name_database='avilist',
    source='https://www.avilist.org/checklist/v2026/',
    file_path='data/raw/AviList-v2026-20Oct2026-extended-version.xlsx'
)
avilist.load_data()

print(avilist.raw_data)


avonet = Dataset(
    name_database='avonet',
    source='https://figshare.com/s/b990722d72a26b5bfead',
    file_path='data/raw/AVONET Supplementary dataset 1.xlsx'
)

avonet.load_data()

birdbase = Dataset(
    name_database='birdbase',
    source='https://doi.org/10.6084/m9.figshare.27051040',
    file_path='data/raw/BIRDBASE v2025.1 Sekercioglu et al. Final.xlsx'
)

birdbase.load_data()
