from nymphes_midi.NymphesPreset import NymphesPreset
from nymphes_osc import NymphesOSC
from pathlib import Path
import csv


def generate_parameters_map_csv_file_for_juce(filepath):
    """
    Generate a CSV file containing a full listing of all Nymphes
    parameters and their OSC messages, as well as value types and
    min/max values, for use in creating a remote control plugin with
    JUCE.
    Periods in parameter names are replaced with underscores, as some
    plugin hosts don't like to see periods in parameter IDs.
    :param filepath: Str or Path. This is where the CSV file will be written. Raises an Exception if empty.
    """
    if filepath is None:
        raise Exception("filepath was None")

    if len(filepath) == 0:
        raise Exception("Filepath is empty")

    # Make sure filepath is a Path object, and expand tilde into
    # the home folder path (if present). This might be important
    # on some systems.
    filepath = Path(filepath).expanduser()

    p = NymphesPreset()

    param_names = p.all_param_names()

    # This will be a list of dicts, one for each row in the
    # CSV file
    rows = []

    for param_name in param_names:
        this_row_dict = {}

        this_row_dict['nymphes-osc parameter name'] = param_name

        this_row_dict['parameter id'] = param_name.replace('.', '_')

        section = p.section_for_param(param_name).upper()
        feature = p.feature_for_param(param_name).upper()
        mod_source = f" {p.mod_source_for_param_name(param_name).upper()}" if p.mod_source_for_param_name(param_name) is not None else ''
        display_name = f"{section} {feature}{mod_source}".replace("_", " ")
        this_row_dict['display name'] = display_name

        this_row_dict['osc address'] = NymphesOSC.osc_address_from_parameter_name(param_name)

        this_row_dict['value type'] = "float" if p.type_for_param_name(param_name) == float else "int"
        
        this_row_dict['min value'] = p.min_val_for_param_name(param_name)
        this_row_dict['max value'] = p.max_val_for_param_name(param_name)
        
        rows.append(this_row_dict)

    with open(filepath, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
