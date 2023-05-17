# Docanno-Pre-label
Docanno pre labeling scritps 
convert_doccano_to_AP.py 
==============
version 2.0.0
date: 2022-10-24


Change history
==============



Prerequisites:
==============
* Python has been installed and can be found in path
* Poetry has been installed and can be found in path


Installation:
=============
1. Extract the package to a folder of your choice.
2. Double click "setup.bat". Setup.bat will 
	a) open windows command prompt (CMD),
	b) create a poetry environment, 
	c) install python dependencies in the newly created environment
	d) finally run the command "poetry run python convert_doccano_to_AP.py", which should show the standard help text 
       indicating successful installation (+ a note about missing input file and label file). 


Usage: 
======
    poetry run python convert_doccano_to_AP.py <input_text_file.jsonl> <ap_label_file.json> 
	                                 [--out <upload_file_name; default = "output/ner_upload.json">]
									 [--remove | --no-remove]

The command converts a Doccano input file with NER labeling and saves results in "ner_upload.json" (default name) file in folder "output" (default folder) to be uploaded into your AP project. 
An Annotation Platform final results file containing at least one annotation for each label from the project that the results are to be uploaded to is used as the second input. 
Items with no "expected_entities" items (suggestions) are removed and saved in files "removed_items_ap.json" (AP upload format) and "removed_items_human_readable.json" (human readable format similar to Doccano input). A summary is saved as "summary.csv".


Supported Entity Types
======================
Any that are tagged in the AP label file
