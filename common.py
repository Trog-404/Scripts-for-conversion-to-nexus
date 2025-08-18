import os
import re
import datetime
import json
import h5py
from pathlib import Path
import tifffile as tf
import numpy as np

def create_group_to_fill(TYPE, where, name):
    group=where.create_group(name)
    group.attrs["NX_class"]=TYPE
    return group

def write_data(dati, where):
    for row in dati:
        if (isinstance(dati[row], str) and row != "m_def") or isinstance(dati[row], (int, float, bool)):
            where.create_dataset(row, data=dati[row])
        elif isinstance(dati[row], dict):
            if dati[row].keys() == {"value", "unit", "direction"}:
                where.create_dataset(row, data=dati[row]["value"])
                where[row].attrs["units"]=dati[row]["unit"]
                where[row].attrs["direction"] = dati[row]["direction"]
            elif dati[row].keys() <= {"value", "unit"}:
                where.create_dataset(row, data=dati[row]["value"])
                where[row].attrs["units"]=dati[row]["unit"]
            elif all(isinstance(x, str) for x in dati[row].values()) and "m_def" not in dati[row].keys():
                values= list(dati[row].values())
                keys=list(dati[row].keys())
                nome_dataset = keys[0]
                valore_dataset = values[0]
                where.create_dataset(nome_dataset, data= valore_dataset)
                for attr, inst in zip(keys[1:], values[1:]):
                    where[nome_dataset].attrs[attr]=inst
            elif "m_def" in dati[row].keys():
                newwhere=create_group_to_fill(dati[row]["m_def"], where, row)
                write_data(dati[row], newwhere)

def write_from_json(json_input, where):
    with open(json_input, "r", encoding="utf-8") as file:
        dati = json.load(file)
        write_data(dati, where)

def aprire_jsons(directory, entry):
    for file in os.listdir(directory):
        if Path(file).suffix == ".json" and "entry" in file:
            write_from_json(os.path.join(directory, file), entry)

    for file in os.listdir(directory):
        if Path(file).suffix == ".json" and "sample" in file:
            sample=create_group_to_fill("NXsample", entry, "sample")
            write_from_json(os.path.join(directory, file), sample)
        if Path(file).suffix == ".json" and "user" in file:
            user=create_group_to_fill("NXuser", entry, "user")
            write_from_json(os.path.join(directory, file), user)
        if Path(file).suffix == ".json" and "instrument" in file:
            instr=create_group_to_fill("NXinstrument", entry, "instrument")
            write_from_json(os.path.join(directory, file), instr)