from os import path, getcwd
import pandas as pd
import sys

"""
Created on Fri Jul 22, 2022
Modified on Fri Oct 21, 2022

@author: markus.enkvist
"""


# ["id", "text", "label", "expected_entities", "labelled_entities"]
class DoccanoFile:
    def __init__(self, filepath, remove):
        self.remove = remove
        self.filepath = filepath
        self.total = 0
        self.removed_items = []
        self.no_id_items = []
        self.no_text_items = []
        self.no_annotation_items = []
        self.no_suggestion_items = []
        self.no_original_annotation_items = []
        self.removal_log = []
        self.items = self.__read()

    def __read(self) -> dict:
        try:
            json_df = pd.read_json(self.filepath, lines=True, encoding='utf-8', encoding_errors='strict')

        except FileNotFoundError:
            filepath = path.join(getcwd() + self.filepath)
            try:
                json_df = pd.read_json(filepath, lines=True, encoding='utf-8', encoding_errors='strict')

            except FileNotFoundError as e:
                print("Error reading file. Please check file path argument.")
                raise FileNotFoundError(e)
        # print("In __read setup", self.remove)  # debug
        doccano_items = []
        counter = 0  # count input
        output_counter = 0  # count output
        no_id_counter = 0  # count items with no id
        no_text_counter = 0  # count items with blank text field
        no_label_counter = 0  # count items with no labels
        no_labelled_entities_counter = 0  # count items with no labelled_entities
        no_expected_entities_counter = 0  # count items with no expected entities

        # case with remove == True
        if self.remove is True:
            try:
                # print("In __read True case", self.remove)  # debug
                print("\nUsing default option --remove. Including only items with suggestions in output.\n")
                for row in json_df.itertuples():
                    counter = counter + 1
                    # cases without id
                    if row.id is None:
                        no_id_counter = no_id_counter + 1
                        self.no_id_items.append(row)
                        row_dict = {"key": row.id,
                                    "text": row.text,
                                    "expected_entities": row.expected_entities,
                                    "labelled_entities": row.labelled_entities}
                        self.removed_items.append(row_dict)
                        self.removal_log.append("Item REMOVED.\tLine {}.\tNo ID found for item id: {}.".format(counter, row.id))
                        print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                              "labelled entities: ", row.labelled_entities)

                    # cases without text
                    if row.text is None:
                        no_text_counter = no_text_counter + 1
                        self.no_text_items.append(row)
                        row_dict = {"key": row.id,
                                    "text": row.text,
                                    "expected_entities": row.expected_entities,
                                    "labelled_entities": row.labelled_entities}
                        self.removed_items.append(row_dict)
                        self.removal_log.append("Item REMOVED.\tLine {}.\tNo text found for item id: {}".format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)


                    # cases with no listed labels
                    if len(row.label) == 0 or row.label is None:
                        no_label_counter = no_label_counter + 1
                        self.no_annotation_items.append(row)
                        self.removal_log.append(
                            "BLANK ITEM.\tLine {}.\tNo labels found for item id: {}.".format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)

                        # cases with no labelled entities

                    if len(row.labelled_entities) == 0 or row.labelled_entities is None:
                        no_labelled_entities_counter = no_labelled_entities_counter + 1
                        self.no_original_annotation_items.append(row)
                        self.removal_log.append("NOT removed.\tLine {}. \tNo labelled entities found for item id: {}."
                                                .format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)

                    # cases with no corrections aka expected entities
                    if len(row.expected_entities) == 0 or row.expected_entities is None:
                        no_expected_entities_counter = no_expected_entities_counter + 1
                        self.no_suggestion_items.append(row)
                        row_dict = {"key": row.id,
                                    "text": row.text,
                                    "expected_entities": row.expected_entities,
                                    "labelled_entities": row.labelled_entities}
                        self.removed_items.append(row_dict)
                        self.removal_log.append("Item REMOVED.\tLine {}.\tNo expected entities found for item id: {}."
                                                .format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)

                    else:
                        row_dict = {"key": row.id,
                                    "text": row.text,
                                    "expected_entities": row.expected_entities,
                                    "labelled_entities": row.labelled_entities}
                        doccano_items.append(row_dict)
                        output_counter = output_counter + 1

            except AttributeError:
                print("\n\n*****************\nERROR. A Doccano item appears to be missing an expected field.\n"
                      "Check row #", counter,
                      " in the input file.\nPlease open input file and check the format.\n*****************\n\n")
                raise

        # case with remove == False
        elif self.remove is False:
            try:
                # print("In __read False case", self.remove)  # debug
                print("Using option --no-remove. Including all items in output.")
                for row in json_df.itertuples():
                    counter = counter + 1
                    # cases without id
                    if row.id is None:
                        no_id_counter = no_id_counter + 1
                        self.no_id_items.append(row)
                        self.removal_log.append(
                            "NOT removed.\tLine {}.\tNo ID found for item id: {}.".format(counter, row.id))
                        print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                              "labelled entities: ", row.labelled_entities)

                    # cases without text
                    if row.text is None:
                        no_text_counter = no_text_counter + 1
                        self.no_text_items.append(row)
                        self.removal_log.append(
                            "NOT removed.\tLine {}.\tNo text found for item id: {}".format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)

                    # cases with no listed labels
                    if len(row.label) == 0 or row.label is None:
                        no_label_counter = no_label_counter + 1
                        self.no_annotation_items.append(row)
                        self.removal_log.append(
                            "NOT removed.\tLine {}.\tNo labels found for item id: {}.".format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)

                    # cases with no labelled entities
                    if len(row.labelled_entities) == 0 or row.labelled_entities is None:
                        no_labelled_entities_counter = no_labelled_entities_counter + 1
                        self.no_original_annotation_items.append(row)
                        self.removal_log.append("NOT removed.\tLine {}.\tNo labelled entities found for item id: {}."
                                                .format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)

                    # cases with no corrections aka expected entities
                    if len(row.expected_entities) == 0 or row.expected_entities is None:
                        no_expected_entities_counter = no_expected_entities_counter + 1
                        self.no_suggestion_items.append(row)
                        self.removal_log.append("NOT removed.\tLine {}.\tNo expected entities found for item id: {}."
                                                .format(counter, row.id))
                        # print("Id: ", row.id, "text: ", row.text, "expected entities: ", row.expected_entities,
                        #       "labelled entities: ", row.labelled_entities)

                    row_dict = {"key": row.id,
                                "text": row.text,
                                "expected_entities": row.expected_entities,
                                "labelled_entities": row.labelled_entities}
                    doccano_items.append(row_dict)
                    output_counter = output_counter + 1
            except AttributeError:
                print("\n\n*****************\nERROR. A Doccano item appears to be missing an expected field.\n"
                      "Check row #", counter,
                      " in the input file.\nPlease open input file and check the format.\n*****************\n\n")
                raise

        else:
            print("Please report this error to author. Boolean remove variable was neither True or False")
            print(self.remove)
            raise ValueError

        self.total = counter

        return doccano_items

    # needed for iterable
    def __iter__(self):
        return iter(self.items)

    def is_empty(self):
        if len(self.items) == 0:
            return True
        return False

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return str(self.items)

    # needed for subscriptable
    def __getitem__(self, key):
        return self.items[key]

    def get_data(self):
        return self.items
