import requests
from bs4 import BeautifulSoup
import pandas as pd

# Pull HTML from higher level taxa page and pull tages with names and links to
# pages with species lists.
top_url = "https://www.marlin.ac.uk/species/"
top_page = requests.get(top_url)
top_soup = BeautifulSoup(top_page.content, "html.parser")
top_results = top_soup.find_all("div", class_ = "media-body")

# Initialize empty lists to hold higher level taxa names and URLs to species
# list page for the taxa. 
taxa_names = []
taxa_urls = []

# Iterate through HTML and append taxa names to taxa_names list.
for result in top_results:
    name = result.text.strip()
    taxa_names.append(name)

# Iterate through HTML and append URL to species list page for each taxa to the
# taxa_urls list.
for result in top_results:
    links = result.find_all("a")
    for link in links:
        link_url = link["href"]
        taxa_urls.append(link_url)

# Subset to filter some records that don't capture taxa name/URL.
taxa_names = taxa_names[0:20]
taxa_urls = taxa_urls[0:20]

# Initialize empty lists to hold lists of species names and URLs for individual
# species pages for each taxa.
species_names = []
species_urls = []

# For each species within a higher order taxa, pull the species name and append
# to a temporary list. Once complete, append this list to the species_names
# list.
for taxa in range(0, len(taxa_names)):
    url = taxa_urls[taxa]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_ = "media-body")
    species = []
    #Skip the first row, since it will be the higher level order name
    for name in range(1,len(results) - 1):
        temp = results[name].text.strip()
        species.append(temp)
    species_names.append(species)

# For each species within a higher order taxa, pull the species' url and append
# to a temporary list. Once complete, append this list to the species_urls
# list.
for taxa in range(0, len(taxa_names)):
    url = taxa_urls[taxa]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all("div", class_ = "media-body")
    urls = []
    #Skip the first row, since it will be the higher level order name
    for name in range(1,len(results) - 1):
        links = results[name].find_all("a")
        for link in links:
            link_url = link["href"]
            urls.append(link_url)
    species_urls.append(urls)

# Initialize an empty list to hold lists of identifying features for each
# species.
species_ids = []

# For each taxa, go to its individual species pages, extract identifying
# features list, and append it to a temporary list. Once complete, append to
# the species_id list.
for taxa in range(0, len(species_names)):
    ids = []
    for urls in range(0, len(species_urls[taxa])):
        url = species_urls[taxa][urls]
        page = requests.get(url)       
        soup = BeautifulSoup(page.content, "html.parser")
        results_one = soup.find_all("div", class_ = "media-body")
        results_two = results_one[5].find_all("li")
        id_list = [n.text for n in results_two]
        ids.append(id_list)
    species_ids.append(ids)

# Create a df from the lists to hold all the info.
df = pd.DataFrame(columns = ["Taxa", "Species", "IDNotes", "Image"])
counter = -1
for taxa in range(0, len(species_names)):
    for name in range(0, len(species_names[taxa])):
        counter = counter + 1
        df.loc[counter] = [taxa_names[taxa], species_names[taxa][name], species_ids[taxa][name], ""]

# For each species, download its image to the WebScrapeImage directory.
for taxa in range(0, len(species_names)):
    for urls in range(0, len(species_urls[taxa])):
        url = species_urls[taxa][urls]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results_one = soup.find_all("div", class_ = "item active")
        results_two = results_one[0].find_all("img")
        results_two[0]["src"]
        image_url = "https://www.marlin.ac.uk" + results_two[0]["src"]
        r = requests.get(image_url)
        with open("/home/skirnir314/EECMSc/CreateUKMarineSpeciesIDGuide/WebScrapeImages/" + species_names[taxa][urls].replace(" ","") + ".jpg", 'wb') as f:
            f.write(r.content)

# Write a CSV of the taxa we care about
df[df["Taxa"].isin(list(taxa_names[i] for i in [3, 4, 5, 6, 7, 8, 9, 11, 12]))].to_csv("/home/skirnir314/EECMSc/PlayingAround/filtered_taxa.csv")
