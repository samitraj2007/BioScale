"""
NHANES Metadata Schema.

This module will contain:
- Variable labels and descriptions
- Units of measurement
- Value mappings for categorical variables (e.g., sex codes)
- Data quality thresholds
- Derived variable formulas

TODO: Load from YAML/JSON configuration file at:
  - backend/etl/nhanes_metadata.yaml
  - Or generated from NHANES documentation

For now, this serves as a placeholder for future metadata loading.
"""

# TODO: Define metadata dictionaries here
# Example structure:

VARIABLE_METADATA = {
    # Demographic variables
    "RIDAGEYR": {
        "label": "Age at Screening Exam",
        "units": "years",
        "type": "numeric",
    },
    "RIDSEX": {
        "label": "Gender",
        "units": "categorical",
        "type": "categorical",
        "values": {1: "Male", 2: "Female"},
    },
    "RIDRETH1": {
        "label": "Race/Hispanic Origin",
        "units": "categorical",
        "type": "categorical",
        "values": {
            1: "Mexican American",
            2: "Other Hispanic",
            3: "Non-Hispanic White",
            4: "Non-Hispanic Black",
            5: "Other Race",
        },
    },
    # Body measurements
    "BMXBMI": {
        "label": "Body Mass Index",
        "units": "kg/m^2",
        "type": "numeric",
    },
    "BMXWAIST": {
        "label": "Waist Circumference",
        "units": "cm",
        "type": "numeric",
    },
    # Lab values
    "LBXALB": {
        "label": "Albumin",
        "units": "g/dL",
        "type": "numeric",
    },
    "LBXCR": {
        "label": "Creatinine",
        "units": "mg/dL",
        "type": "numeric",
    },
    "LBXGLU": {
        "label": "Fasting Glucose",
        "units": "mg/dL",
        "type": "numeric",
    },
    "LBXCRP": {
        "label": "C-Reactive Protein",
        "units": "mg/L",
        "type": "numeric",
    },
    "LBXWBC": {
        "label": "White Blood Cell Count",
        "units": "10^3/uL",
        "type": "numeric",
    },
    "LBXRDW": {
        "label": "Red Cell Distribution Width",
        "units": "%",
        "type": "numeric",
    },
}


def get_variable_label(var_name: str) -> str:
    """
    Get human-readable label for a variable.
    
    Parameters
    ----------
    var_name : str
        Variable name (e.g., "LBXALB").
    
    Returns
    -------
    str
        Label, or the variable name if not found.
    """
    if var_name in VARIABLE_METADATA:
        return VARIABLE_METADATA[var_name].get("label", var_name)
    return var_name


def get_variable_units(var_name: str) -> str:
    """
    Get units for a variable.
    
    Parameters
    ----------
    var_name : str
        Variable name (e.g., "LBXALB").
    
    Returns
    -------
    str
        Units, or empty string if not found.
    """
    if var_name in VARIABLE_METADATA:
        return VARIABLE_METADATA[var_name].get("units", "")
    return ""


# TODO: Load from YAML/JSON file on module import
# Example YAML structure:
#
# variables:
#   RIDAGEYR:
#     label: "Age at Screening Exam"
#     units: "years"
#     type: "numeric"
#   RIDSEX:
#     label: "Gender"
#     units: "categorical"
#     type: "categorical"
#     values:
#       1: "Male"
#       2: "Female"
