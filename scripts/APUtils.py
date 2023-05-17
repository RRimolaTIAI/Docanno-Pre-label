# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 11:52:44 2022

@author: jari.perakyla
"""
import uuid


class APAnnotation:
    
    def __init__(self, label_custom_key, quote, start, end, comment):
        self.comment = comment
        self.end = end
        self.quote = quote
        self.start = start
        self.label_custom_id = label_custom_key
        self.label_id = None
        self.label_text = None
        self.uuid = str(uuid.uuid1())

    def as_dict(self):
        return({
            "comment": self.comment,
            "end": self.end,
            "quote": self.quote,
            "start": self.start,
            "label_custom_id": self.label_custom_id,
            "label_id": self.label_id,
            "label_text": self.label_text,
            "uuid": self.uuid
        })


class APItem:
    def __init__(self, key, inputs, outputs):
        self.key = str(key)
        self.inputs = inputs
        self.outputs = outputs
        
    def add_annotation(self, annotation):
        if len(self.outputs) > 0:
            self.outputs[0]["annotations"].append(annotation.as_dict())
        else:
            self.outputs = [{"annotations": [annotation.as_dict()]}]

    def as_dict(self):
        # inputs_dict = [i.as_dic() for i in self.inputs]
        # outputs_dict = [o.as_dict() for o in self.outputs]
        return({
            "key": self.key,
            "inputs": self.inputs,
            "outputs": self.outputs})
