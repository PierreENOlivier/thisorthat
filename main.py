from thisorthat import ClassicAPI, TraitScrapper

api = ClassicAPI()

valid_species = api.search_species("Psittacus erithacus")
print(valid_species)

scrapper = TraitScrapper()
parrot = scrapper.scrape_species(valid_species['id'])
print(parrot)
