# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 11:18:01 2022

@author: jari.perakyla
"""

import json
import pandas as pd


class NERResultFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.result = self.__read()

    def __read(self):
        try:
            with open(self.file_name, encoding="utf-8") as f:
                result = json.load(f)
        except FileNotFoundError:
                result = None
        
        # TODO: Other read error
        return result

    def get_label_info(self):
        label_custom_id_error = False
        labels = pd.DataFrame(columns=["label_id", "label_custom_id", "label_text"])

        for item in self.result:
            outputs = item["outputs"]
            if outputs:
                for output in outputs:
                    annotations = output["annotations"]
                    if len(annotations) > 0:
                        for annotation in annotations:
                            if (
                                not annotation["label_custom_id"]
                                and annotation["label_text"]
                            ):
                                if not label_custom_id_error:
                                    #print(
                                    #    "    Warning: Custom Key (label_custom_id) is empty, using Class Name (label_text) as class ID. \n             It is recommended to use standardized Custome Key and localized Class Name."
                                    #)
                                    label_custom_id_error = True
                                annotation["label_custom_id"] = annotation["label_text"]
                            elif annotation["label_custom_id"] is None:
                                exit("label_custom_id is empty. ")
                            labels = pd.concat(
                                [
                                    labels,
                                    pd.DataFrame(
                                        {
                                            "label_id": [annotation["label_id"]],
                                            "label_custom_id": [
                                                annotation["label_custom_id"]
                                            ],
                                            "label_text": [annotation["label_text"]],
                                        }
                                    ),
                                ],
                                ignore_index=True,
                                axis=0,
                            )
                            
        # Keep only unique labels
        labels_unique = labels.drop_duplicates(subset=["label_custom_id"])
        labels_unique.set_index("label_custom_id", drop=False, inplace=True)

        return labels_unique
