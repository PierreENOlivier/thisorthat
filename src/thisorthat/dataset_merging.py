import pandas as pd
from pathlib import Path

from openpyxl.chart import reference

from thisorthat.utils import get_project_root
from functools import reduce

ROOT = get_project_root()
print(ROOT)

IUCN_STATUS_ORDER = []

NCHAR_AVIBASE_SHORT = len("A20878F0")

NCHAR_AVIBASE_LONG = len("A20878F0EBC3724F")

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
        'col_types': {
            'beak_length_mm': 'float64',
            'wing_length_mm': 'float64',
            'tail_length_mm': 'float64',
            'body_mass_gr': 'float64',
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
            'Order': 'order',
            'Family AviList v1 2025': 'family',
            'Average Mass': 'avg_body_mass',
            'Clutch_Max': 'max_clutch_size',
            'NormMax': 'highest_elevation',
            'Incu1': 'shortest_incubation',
            'Incu2': 'longest_incubation',
            'Fldg1': 'shortest_fledging',
            'Fldg2': 'longest_fledging'
        },
        'col_types': {
            'avg_body_mass': 'float64',
            'max_clutch_size': 'int64',
            'highest_elevation': 'int64',
            'shortest_incubation': 'int64',
            'longest_incubation': 'int64',
            'shortest_fledging': 'int64',
            'longest_fledging': 'int64',
        },
        'transform': {},
        'col_keep': [
            'order',
            'family',
            'scientific_name',
            'avg_body_mass',
            'max_clutch_size',
            'highest_elevation',
            'shortest_incubation',
            'longest_incubation',
            'shortest_fledging',
            'longest_fledging'
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
            'BIRDS OF THE WORLD URL': 'birdworld_url',
            'AVIBASE ID': 'avibase_id',
        },
        'col_types': {},
        'transform': {},
        'col_keep': [
            'avibase_id',
            'order',
            'family',
            'scientific_name',
            'common_name',
            'red_list',
            'datazone_url',
            'birdworld_url'
        ]

    },
    'BIRDNET': {
        'rename': {
            'avibase_id': 'avibase_id',
            'commonness': 'commonness',
        },
        'col_types': {
            'commonness': 'float64',
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
}

def load_avonet(dataset):
    col_mapping = COLUMN_MAPPINGS[dataset.name_database.upper()]

    data = pd.read_excel(
        io=ROOT / dataset.file_path,
        sheet_name='AVONET1_BirdLife'
    )

    data = data.rename(columns=col_mapping['rename'])

    # Extract Avibase ID
    data['avibase_id'] = data['avibase_id'].astype("string").str[-NCHAR_AVIBASE_SHORT:]

    data = format_type_columns(data, col_mapping['col_types'])
    return data.loc[:, col_mapping['col_keep']].copy()

def load_birdbase(dataset):
    col_mapping = COLUMN_MAPPINGS[dataset.name_database.upper()]

    data = pd.read_excel(
        io=ROOT / dataset.file_path,
        sheet_name='Data',
        header=1
    )

    data["scientific_name"] = (
        data["Genus"].astype("string")
        + " "
        + data["Species"].astype("string")
    )

    data = data.rename(columns=col_mapping['rename'])
    data = data.loc[:, col_mapping['col_keep']].copy()
    data = format_type_columns(data, col_mapping['col_types'])
    return data.loc[:, col_mapping['col_keep']].copy()

def load_birdnet(dataset):
    col_mapping = COLUMN_MAPPINGS[dataset.name_database.upper()]

    data = pd.read_csv(
        ROOT / dataset.file_path,
        sep=',',
        header=0
    )

    data = data.rename(columns=col_mapping['rename'])
    data['avibase_id'] = data['avibase_id'].astype("string").str[:NCHAR_AVIBASE_SHORT]

    data.dropna(subset=['image_url'], inplace=True)
    data = format_type_columns(data, col_mapping['col_types'])
    return  data.loc[data['record_type'] == 'species', col_mapping['col_keep']].copy()


def load_avilist(dataset):
    col_mapping = COLUMN_MAPPINGS[dataset.name_database.upper()]

    data = pd.read_excel(
        io=ROOT / dataset.file_path,
        sheet_name='AviList v2026',
    )
    data = data.rename(columns=col_mapping['rename'])
    data['avibase_id'] = data['avibase_id'].str.split('-', expand=True)[1]
    data = format_type_columns(data, col_mapping['col_types'])
    return data.loc[data['RANK'].eq('species'), col_mapping['col_keep']].copy()

LOADER_REGISTRY = {
    'AVONET': load_avonet,
    'BIRDBASE': load_birdbase,
    'AVILIST': load_avilist,
    'BIRDNET': load_birdnet

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
    VALID_CATEGORIES = {"bird", "fish"}

    def __init__(
            self,
            merged_dataset,
            source_datasets=None,
            category=None,
    ):
        self.merged_dataset = merged_dataset
        self.source_datasets = source_datasets or []

        category = category.strip().lower()
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category {category!r}. "
                f"Choose one of: {sorted(self.VALID_CATEGORIES)}"
            )

        self.category = category

    @classmethod
    def merge_datasets(
            cls,
            ref_dataset,
            other_sources,
            on,
            category=None,
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

        dataset_list = other_sources.insert(0, ref_dataset)

        # merged = reduce(
        #     lamdba left, right:
        #         left.
        # )

        # return cls(
            # merged_dataset=merged,
            # source_datasets=[ref_dataset, *other_sources],
            # category=category
        # )

# Taxonomy Resolution
class TaxonomyResolver:
    def __init__(self, reference_dataset):
        self.reference_dataset = reference_dataset

    def add_avibase_id(self, data):
        reference = self.reference_dataset[
            ["avibase_id", "scientific_name"]
        ].copy()

        reference['merge_key'] = normalize_species_name(
            reference['scientific_name'],
        )

        result = data.copy()
        result['merge_key'] = normalize_species_name(
            result['scientific_name'],
        )

        return result.merge(
            reference[["merge_key", "avibase_id"]],
            on="merge_key",
            how="left",
        )

    @classmethod
    def from_file(
            cls,
            file_path
    ):
        """
        Load a reference taxonomy to resolve species
        :param file_path:
        :return:
        """
        # Unsure what is a good reference
        # Need reference with synonyms
        pass

def normalize_species_name(series):
    return (
        series.astype("string")
        .str.normalize("NFKC")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.casefold()
    )

# Helpers
def format_type_columns(
        dataset,
        type_mapping:dict
):
    return dataset.astype(type_mapping)

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

birdnet = Dataset(
    name_database='birdnet',
    source='https://birdnet.cornell.edu/taxonomy/download',
    file_path='data/raw/birdnet_taxonomy_0.4-Oct2026.csv'
)

birdnet.load_data()



ConsolidatedDataset.merge_datasets(
    avilist,
    [birdnet, avonet, birdbase],
    category="bird"
)
