# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 10:43:32 2022
Modified on Fri Oct 21, 2022

@authors: jari.perakyla, markus.enkvist
"""

# TODO: fix AP label source file to match Doccano labels
# TODO: AP file uses "DIMENSIONS" but Doccano uses "DIMENSION"

from pathlib import Path
import argparse

import pandas as pd
from collections import Counter
from datetime import datetime
import json
import sys
from scripts.NER.NERResultFile import NERResultFile
from scripts.NER.NERUploadFile import NERUploadFile
from scripts.APUtils import APAnnotation, APItem
from scripts.DoccanoFile import DoccanoFile


def main():
    print('Doccano JSONL to AP JSON file converter 2.0')
    # Create CLI using argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("doccano_file_path", help="Path to Doccano JSONL file")
    parser.add_argument("ap_tag_file_path", help="Path to AP project specific tag file")
    parser.add_argument("--out", default='output/ner_upload.json', help="Output filename")
    parser.add_argument("--remove", default=True, action=argparse.BooleanOptionalAction,
                        help="Remove/keep items which have no suggestions")
    args = parser.parse_args()

    doccano_filepath = Path(args.doccano_file_path)
    ap_tags_filepath = Path(args.ap_tag_file_path)
    outpath = Path(args.out)
    removed_items_ap_path = Path('output/removed_items_ap.json')
    removed_items_human_path = Path('output/removed_items_human_readable.json')
    summary_filepath = Path('output/summary.csv')
    remove = args.remove

    if doccano_filepath.is_file():
        file_extension = doccano_filepath.suffix
        if file_extension != ".jsonl":
            print("Error: Doccano input file extension is not JSONL: ", file_extension)
            sys.exit()

        if ap_tags_filepath.is_file():
            file_extension = ap_tags_filepath.suffix
            if file_extension != ".json":
                print("Error: AP project label input file extension is not JSON: ", file_extension)
                sys.exit()
        else:
            print("The AP project label file does not exist. Please check the input file argument.")
            sys.exit()

        # Read label info (=label_id etc.)
        source_file = DoccanoFile(doccano_filepath, remove)
        # write removal log to file
        try:
            with open('removal_log.txt', 'w', encoding='utf-8') as f:
                print(datetime.now(), file=f)
                for item in source_file.removal_log:
                    f.write(f"{item}\n")
        except Exception as e:
            print(e)
            print("Warning! Unable to save removal log to file.")

        # write summary to CSV file
        if remove == 1:
            summary = [
                ['Total items',
                 source_file.total],
                ["Output items",
                 len(source_file.items),
                 round((len(source_file.items) / source_file.total) * 100, 2)],
                ["Removed items total",
                 len(source_file.removed_items),
                 round((len(source_file.removed_items) / source_file.total) * 100, 2),
                 True],
                ["Items with no suggestions (expected entities)",
                 len(source_file.no_suggestion_items),
                 round((len(source_file.no_suggestion_items) / source_file.total) * 100, 2),
                 True],
                ["Items with no annotations at all, a subset of above",
                 len(source_file.no_annotation_items),
                 round((len(source_file.no_annotation_items) / source_file.total) * 100, 2),
                 True],
                ["Items with no id",
                 len(source_file.no_id_items),
                 round((len(source_file.no_id_items) / source_file.total) * 100, 2),
                 True],
                ["Items with no text",
                 len(source_file.no_text_items),
                 round((len(source_file.no_text_items) / source_file.total) * 100, 2),
                 True],
                ["Items with no no original annotations (labelled_entities)",
                 len(source_file.no_original_annotation_items),
                 round((len(source_file.no_original_annotation_items)/source_file.total) * 100, 2),
                 False]
            ]
        else:
            summary = [
                ['Total items',
                 source_file.total],
                ["Output items",
                 len(source_file.items),
                 round((len(source_file.items) / source_file.total) * 100, 2)],
                ["Removed items total",
                 len(source_file.removed_items),
                 round((len(source_file.removed_items) / source_file.total) * 100, 2),
                 False],
                ["Items with no suggestions (expected entities)",
                 len(source_file.no_suggestion_items),
                 round((len(source_file.no_suggestion_items) / source_file.total) * 100, 2),
                 False],
                ["Items with no annotations at all, a subset of above",
                 len(source_file.no_annotation_items),
                 round((len(source_file.no_annotation_items) / source_file.total) * 100, 2),
                 False],
                ["Items with no id",
                 len(source_file.no_id_items),
                 round((len(source_file.no_id_items) / source_file.total) * 100, 2),
                 False],
                ["Items with no text",
                 len(source_file.no_text_items),
                 round((len(source_file.no_text_items) / source_file.total) * 100, 2),
                 False],
                ["Items with no original annotations (labelled_entities)",
                 len(source_file.no_original_annotation_items),
                 round((len(source_file.no_original_annotation_items) / source_file.total) * 100, 2),
                 False]
            ]

        summary_df = pd.DataFrame(summary, columns=['Label', 'Count', 'Percentage (%)', 'Removed'])
        try:
            summary_df.to_csv(summary_filepath, index=False)

        except PermissionError:
            print("\nError. Unable to save summary to summary.csv as it is open in another program.\n"
                  "Please close the file and try again.\n")
            sys.exit()
        except IOError:
            print("Error saving summary to csv.")
            raise

        try:
            with open("output/summary.txt", 'w', encoding='utf-8') as f:
                print(datetime.now(), file=f)
                print("\nSUMMARY", file=f)
                print("Total items: ", source_file.total, file=f)
                print("Output items: ", len(source_file.items), file=f)
                print("Removed items: ", len(source_file.removed_items), file=f)
                print("\n\nDetails", file=f)
                if remove == 1:
                    print("Removed:", file=f)
                    print("Items with no expected entities (no suggestions): ",
                          len(source_file.no_suggestion_items), file=f)
                    print("\tItems with no labels (a subset of above): ",
                          len(source_file.no_annotation_items), file=f)
                    print("Items with no id: ",
                          len(source_file.no_id_items), file=f)
                    print("Items with no text: ",
                          len(source_file.no_text_items), file=f)
                    print("\nNot removed:", file=f)
                    print("Items with no labelled entities (no original annotations): ",
                          len(source_file.no_original_annotation_items), file=f)
                else:
                    print("Items with no expected entities (no suggestions): ",
                          len(source_file.no_suggestion_items), file=f)
                    print("\tItems with no labels (a subset of above): ",
                          len(source_file.no_annotation_items), file=f)
                    print("Items with no id: ",
                          len(source_file.no_id_items), file=f)
                    print("Items with no text: ",
                          len(source_file.no_text_items), file=f)
                    print("Items with no labelled entities (no original annotations): ",
                          len(source_file.no_original_annotation_items), file=f)

        except Exception as e:
            print(e)
            print("Warning! Unable to save summary.txt to file.")

        # write removed items to file
        try:
            with open(removed_items_human_path, 'w', encoding='utf-8') as f:
                json.dump(source_file.removed_items, f, indent=1)
        except OSError as e:
            print("ERROR! Failed to write removed items to file.")
            raise e

        # process tags
        ap_tagged_file = NERResultFile(ap_tags_filepath)
        label_info = ap_tagged_file.get_label_info()
        # label_info.to_excel("label_info.xlsx")
        # print(label_info)

        # create upload file
        upload_file = NERUploadFile([], label_info=label_info)
        print("Total items: ", source_file.total)

        for source_item in source_file.items:
            ap_item = APItem(key=source_item["key"], inputs=[{"text": source_item["text"]}], outputs=[])
            for exp_ent in source_item["expected_entities"]:
                ap_annotation = APAnnotation(label_custom_key=exp_ent[2],
                                             start=exp_ent[0],
                                             end=exp_ent[1],
                                             quote=source_item["text"][exp_ent[0]:exp_ent[1]], comment=None)
                ap_item.add_annotation(ap_annotation)
            for lab_ent in source_item["labelled_entities"]:
                ap_annotation = APAnnotation(label_custom_key=lab_ent[2], start=lab_ent[0], end=lab_ent[1],
                                             quote=source_item["text"][lab_ent[0]:lab_ent[1]], comment=None)
                ap_item.add_annotation(ap_annotation)
            upload_file.add_item(ap_item)

        # write upload file or get missing labels if any
        missing_labels = upload_file.write(outpath, write_if_error=False)  # production
        # missing_labels = upload_file.write("test/tmp_out_files/ner_upload_file_true.json",
        #                                    write_if_error=True)  # debugging

        if missing_labels is None:
            print("Conversion done. See output folder for results.")

        # count missing labels and save to file
        elif len(missing_labels) > 0:
            print("Error: Missing annotation labels found:")
            missing_labels_counter = Counter(missing_labels)
            missing_labels_df = pd.DataFrame({"count": missing_labels_counter})
            missing_labels_df.to_csv("labels_not_found.csv")
            print(missing_labels_df)

        # create removed items file
        removed_items_file = NERUploadFile([], label_info=label_info)
        print("Removed items: ", len(source_file.removed_items))

        for removed_item in source_file.removed_items:
            ap_item = APItem(key=removed_item["key"], inputs=[{"text": removed_item["text"]}], outputs=[])
            for exp_ent in removed_item["expected_entities"]:
                ap_annotation = APAnnotation(label_custom_key=exp_ent[2],
                                             start=exp_ent[0],
                                             end=exp_ent[1],
                                             quote=removed_item["text"][exp_ent[0]:exp_ent[1]], comment=None)
                ap_item.add_annotation(ap_annotation)
            for lab_ent in removed_item["labelled_entities"]:
                ap_annotation = APAnnotation(label_custom_key=lab_ent[2], start=lab_ent[0], end=lab_ent[1],
                                             quote=removed_item["text"][lab_ent[0]:lab_ent[1]], comment=None)
                ap_item.add_annotation(ap_annotation)
            removed_items_file.add_item(ap_item)

        # write upload file or get missing labels if any
        removed_items_missing_labels = removed_items_file.write(removed_items_ap_path,
                                                                write_if_error=False)  # production
        # missing_labels = upload_file.write("test/tmp_out_files/ner_upload_file_true.json",
        #                                    write_if_error=True)  # debugging

        if removed_items_missing_labels is None:
            print("Removed items JSON file saved.")

        # count missing labels and save to file
        elif len(removed_items_missing_labels) > 0:
            print("Warning: Missing annotation labels found in removed items:")
            missing_labels_counter = Counter(removed_items_missing_labels)
            missing_labels_df = pd.DataFrame({"count": missing_labels_counter})
            missing_labels_df.to_csv("labels_not_found_in_removed_items.csv")
            print(missing_labels_df)

    else:
        print("The input file does not exist. Please check the input file argument.")
        sys.exit()
    return


if __name__ == "__main__":
    main()
