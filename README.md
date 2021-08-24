## Parsing Simple Wikipedia

This is a  CLI tool that extracts the global counts of uri & surface form pairs from json files in a pages folder.
A redirects file is used to ensure uri's are resolved correctly before storing as a tsv sorted in descending order of count.

### Instructions

The following extra libraries are required:
*fire - https://google.github.io/python-fire/guide/
*ujson - https://github.com/ultrajson/ultrajson
*pandas - https://pandas.pydata.org/

All other libraries used are a part of python's default standard library.

To use the tool run the following command in the CLI:

`python pair_counts.py --in-folder <path-to-data> --out-folder <path-to-counts-destination>` , where
	* `<path-to-data>` corresponds to the data folder , e.g. data
	* `<path-to-counts-destination>` corresponds to a folder that contains a `.tsv` file of the format

```
uri<tab>surface_form<tab>count
```
