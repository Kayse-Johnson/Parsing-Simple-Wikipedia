import fire
import re
import os, ujson, mmap
import pandas as pd

def write_tsv(sorted_list: list, out_folder: str):
    """
    Serialise the data returned by `count_data` into  a tsv file.
    """
    tsv_file_path = os.path.join(out_folder, 'wiki_counts.tsv') # produce file path from out_folder
    unpacked_sorted_list = [] # create an empty list to unpack the (uri, surface_form) tuples and pack them together with the count
    for (url, surface_form), count in sorted_list:
        unpacked_sorted_list.append((url, surface_form, count))
    df = pd.DataFrame(unpacked_sorted_list, columns = ['uri', 'surface_form', 'count']) # parse the unpacked list to a pandas dataframe and write a tsv file
    df.to_csv(tsv_file_path, index=False, sep=' ')

def count_data(count_dicts: dict, redirects: dict):
    """
    Iterate over the links given by `load_page_links` and count them,
    load redirects is used to ensure only valid tuple pairs are saved.
    Returns a list with the structure [(('uri','surface_form'),count),.....]
    """
    total_dict = {} # create an empty dictionary to track all the counted pairs
    for page in count_dicts: # iterate through each dictionary loaded by the generator
        for key in page: # iterate through the keys in each dictionary
            if key[0] in redirects: # if the uri in the yielded dictionary is in redirects then resolve the uri with the correct new key, else assume uri is valid
                new_key = (redirects[key[0]], key[1])
                if new_key in total_dict: # if the new key is present in total__dict update the counter value else create a new entry with the correct new key and update the counter
                    total_dict[new_key] = total_dict.get(new_key) + page.get(key)
                else:
                    total_dict[new_key] = page.get(key)
            else:
                if key in total_dict: # assuming a valid uri/key if it is in total_dict update the counter or otherwise create a new entry
                    total_dict[key] = page.get(key) + total_dict.get(key)
                else:
                    total_dict[key] = page.get(key)
    sorted_count_list = sorted(total_dict.items(), key=lambda x:x[1], reverse=True) # return a sorted list to parse to the write_tsv function
    return sorted_count_list


def load_page_links(pages_folder: str):
    """
    Iterate over each json file in pages folder
    and return some data structure that iterates over a tuple of
    (uri, surface_form, count);
    where count corresponds to the number of times the pair <uri, surface_form>
    occurred in the page (note this is not the global count).
    """
    json_files = os.listdir(pages_folder) # produce list of all json files in the pages folder
    for page in json_files: # iterate through each json file
        dir = os.path.join(pages_folder, page)
        with open(dir,"r") as json_file: # open each file
            with mmap.mmap(json_file.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
                page_contents = ujson.load(mmap_obj)
        pairs_dict = {}
        for annotation in page_contents['annotations']: # iterate through all annotations to parse the uri and surface form data
            if (annotation['uri'],annotation['surface_form']) not in pairs_dict: # if the following key not found in the dict create one, otherwise update the count
                pairs_dict[(annotation['uri'],annotation['surface_form'])]= 1
            else:
                pairs_dict[(annotation['uri'],annotation['surface_form'])]= pairs_dict.get((annotation['uri'],annotation['surface_form'])) + 1
        yield pairs_dict


def load_redirects(redir_path: str):
    """
    Load the redirects file and return a dictionary that 
    adjusts the URI when counting the pairs around each link
    """
    with open(redir_path, "rb") as file:
        redirects_contents = file.read().decode() # read the redirects file
        redirects = re.findall(r'(?<=resource\/).+?(?=>)', redirects_contents) # match all the uri strings and return them as a list
        fake_titles = redirects[::2] # separate the true uri with the redirected uri
        real_titles = redirects[1::2]
        redirects = dict(zip(fake_titles, real_titles)) # return this data as a dictionary
        return redirects



def process_data(in_folder: str, out_folder:str) -> None:
    """
    Consume the data from the input folder to generate the tsv counts in descending order
    to be saved in the out_folder.
    """
    pages_folder = os.path.join(in_folder, 'pages')
    redirects_folder = os.path.join(in_folder, 'redirects.nt')
    redirects = load_redirects(redirects_folder)
    count_dicts = load_page_links(pages_folder)
    sorted_count_list = count_data(count_dicts, redirects)
    write_tsv(sorted_count_list, out_folder)
  

if __name__ == '__main__':
    fire.Fire(process_data)
