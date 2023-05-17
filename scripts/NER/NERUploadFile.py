# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 11:18:01 2022
Modified on September 22, 2022

@authors: jari.perakyla, markus.enkvist
"""

import json


class NERUploadFile:

    def __init__(self, items, label_info=None):
        self.label_info = label_info
        self.items = items

    def __complete_labels(self):

        labels_not_found = []
        counter = 0  # debugging row counter
        no_outputs_counter = 0  # count items with no output
        no_corrections_counter = 0  # count items with no expected entities
        for item in self.items:
            counter = counter + 1
            if len(item.outputs) == 0:
                no_outputs_counter = no_outputs_counter + 1
                # print("Error! Something went wrong on item id: ", item.key, "line: ", counter)
                # print("Yet another empty item")

            if len(item.outputs) > 0:
                try:
                    annotations = item.outputs[0]["annotations"]
                except Exception as e:
                    print("Error! Something went wrong on item id: ", item.key, "line: ", counter)
                    raise e
                if not annotations:
                    raise Exception("NoAnnotationsFoundError: No annotations found.")
                else:
                    for annotation in annotations:
                        try:
                            annotation["label_id"] = self.label_info.at[annotation["label_custom_id"], "label_id"]
                            annotation["label_text"] = self.label_info.at[annotation["label_custom_id"], "label_text"]
                        except KeyError:
                            labels_not_found.append(annotation["label_custom_id"])
                            annotation["label_id"] = "label_id_not_found"
                            annotation["label_text"] = "label_text_not_found"

        # print("Total items: ", counter)
        # print("Items with no outputs: ", no_outputs_counter)
        # print("Items with no corrections: ", no_corrections_counter)

        if len(labels_not_found) > 0:
            return labels_not_found
        else:
            return None

    def add_item(self, item):
        if len(self.items) > 0:
            self.items.append(item)
        else:
            self.items = [item]

    def write(self, file_name, write_if_error=False):

        res = self.__complete_labels()
        j = [d.as_dict() for d in self.items]

        if res is None or write_if_error is True:
            try:
                with open(file_name, "w") as f:
                    json.dump(j, f)
            except OSError as e:
                print("ERROR! Failed to write output JSON file.")
                raise e

        if res is not None:
            return res
        else:
            return None
