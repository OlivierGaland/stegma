

# validate kwargs function (decorator)
#
# kwarg profile: dict
#    keys:
#        ignore (optional): list of items (of type string) : exclude from validation
#        mandatory (optional): list of items (of type string) : those must be provided
#        optional (optional): list of items (of type string or dict): those can be provided
#        exclusive (optional): list of list of items (of type string or dict): list of mutually exclusive items profile
#
#    items:
#        either a string or a dict:
#            string : name of the argument (if mandatory)
#            dict with policy on keys (if optional and not in optional section): 
#                name : mandatory, name of the argument
#                default : optional, default value
#
#    rules that must be followed and validated by the process :
#     - a name argument (either as string or dict) cannot be present in two or more of the ignore, mandatory, optional, exclusive sections at the same time (but can be present in multiple exclusive sections)
#     - ignore section is excluded from the validation process (items are only strings)
#     - any mandatory argument must be provided (items are only strings)
#     - any optional argument can be provided (items can be strings or dicts)
#     - remaining parameters must be checked against all exclusive profiles with the aim to match one and only one profile (successful validation), if several profiles match the validation fails if the ambiguity cannot be resolved (see validation process for details)
#     - if any of the above rules is violated, an documented exception is raised : raise Exception("<verbose error message>")
#
#    validation process :
#     1) check each existing name (either as string or dict) to be present in only one and only one of the ignore, mandatory, optional, exclusive sections at the same time (but can be present in several exclusive sections)
#     2) copy kwargs in a working variable and validate each item type regarding to its section (ignore, mandatory, optional, exclusive)
#     3) discard from the working variable all items that are present in the ignore section
#     4) check that all mandatory arguments are provided and discard them from the working variable
#     5) check for each optional argument : if dict and not present, use default value and add it in the original kwargs, if string do not process. Once done remove all optional arguments from the working variable
#     6) compare remaining arguments of the working variable to all exclusive profiles, it should match one or more profiles, if only one match the validation is successful. Otherwise we should select one of the profiles with the following rules :
#           - if one (or more) profile in included in another profile (i.e. A is a subset of B), we should select the longest one and discard the shortest, if after there is only one elligible profile, the validation is successfull. If there are still more, the validation is failed due to an ambiguity






# validate kwargs function (decorator)
#
# kwarg profile: dict
#    keys:
#        ignore (optional): list of strings — arguments to exclude from validation
#        mandatory (optional): list of strings — arguments that must be provided
#        optional (optional): list of strings or dicts — arguments that can be provided
#        exclusive (optional): list of lists of strings or dicts — mutually exclusive argument profiles
#
#    items:
#        Either a string or a dict:
#            - string: name of the argument (e.g., if mandatory or optional)
#            - dict: describes an argument with additional policy:
#                - name (required): name of the argument
#                - default (optional): default value (only used if the argument is missing)
#
#    Validation rules:
#     - An argument name (whether as a string or as a dict["name"]) must appear in only one of the following sections: ignore, mandatory, optional, or exclusive (but may appear in multiple exclusive profiles).
#     - The ignore section is excluded from all validation (items must be strings).
#     - All mandatory arguments must be present in kwargs (items must be strings).
#     - Optional arguments may be provided (items may be strings or dicts).
#     - Remaining arguments are matched against exclusive profiles. One and only one exclusive profile must match for the validation to succeed.
#       If multiple profiles match and the ambiguity cannot be resolved (see process below), validation fails.
#     - If any rule is violated, raise an Exception with a clear, descriptive message: raise Exception("<verbose error message>")
#
#    Validation process:
#     1) Ensure each argument name (string or dict["name"]) appears in only one of the following: ignore, mandatory, optional, or exclusive (but may appear in multiple exclusive profiles).
#     2) Copy kwargs to a working variable and validate each item type according to its section.
#     3) Remove all items in the ignore section from the working variable.
#     4) Verify that all mandatory arguments are provided, then remove them from the working variable.
#     5) For optional arguments:
#         - If defined as a dict and not present, set its default value into the original kwargs.
#         - If defined as a string, do nothing.
#         Then remove all optional arguments from the working variable.
#     6) Match the remaining arguments against all exclusive profiles:
#         - If exactly one profile matches, validation succeeds.
#         - If multiple profiles match:
#             - Eliminate any profile that is a strict subset of another (e.g., if A ⊂ B, discard A).
#             - If only one profile remains after this filtering, validation succeeds.
#             - If multiple equally eligible profiles remain, raise an exception due to ambiguity.

from functools import wraps

def validate_kwargs(profile):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            ignore = set(profile.get("ignore", []))
            mandatory = set(profile.get("mandatory", []))
            optional = profile.get("optional", [])
            exclusive = profile.get("exclusive", [])

            #print(f"ignore: {ignore}, mandatory: {mandatory}, optional: {optional}, exclusive: {exclusive}")

            # Helper to extract names from strings or dicts
            def extract_name(item):
                return item if isinstance(item, str) else item["name"]

            # Build name to section mapping
            name_to_section = {}

            for section_name, section_items in [
                ("ignore", ignore),
                ("mandatory", mandatory),
                ("optional", optional),
            ]:
                for item in section_items:
                    name = extract_name(item)
                    if name in name_to_section:
                        raise Exception(f"'{name}' is present in multiple sections: {name_to_section[name]} and {section_name}")
                    name_to_section[name] = section_name

            #print(f"name_to_section: {name_to_section}")

            # Exclusive: we allow a name to appear in multiple profiles but not elsewhere
            exclusive_names = set()
            for group in exclusive:
                for item in group:
                    name = extract_name(item)
                    if name in name_to_section:
                        raise Exception(f"'{name}' is present both in exclusive and {name_to_section[name]}")
                    exclusive_names.add(name)

            # Create a working copy of kwargs
            working = dict(kwargs)

            # Step 3: remove ignored items
            for key in ignore:
                working.pop(key, None)

            #print(f"working - ignore: {working}")

            # Step 4: check mandatory
            for key in mandatory:
                if key not in working:
                    raise Exception(f"Missing mandatory argument: {key}")
                working.pop(key)

            #print(f"working - mandatory: {working}")

            # Step 5: handle optional
            optional_names = set()
            for item in optional:
                if isinstance(item, str):
                    optional_names.add(item)
                    working.pop(item, None)
                elif isinstance(item, dict):
                    name = item["name"]
                    optional_names.add(name)
                    if name not in kwargs and "default" in item:
                        kwargs[name] = item["default"]
                    working.pop(name, None)
                else:
                    raise Exception(f"Invalid optional entry: {item}")
                
            #print(f"working - optional: {working}")

            # Step 6: check exclusive
            if len(exclusive) != 0:
                matched_profiles = []

                for group in exclusive:
                    group_required = {extract_name(x) for x in group if isinstance(x, str)}
                    group_optional = {extract_name(x) for x in group if isinstance(x, dict)}
                    if group_required.issubset(working.keys()) and working.keys() <= (group_required | group_optional):
                        matched_profiles.append(group)

                if not matched_profiles:
                    raise Exception(f"No exclusive profile matched with remaining keys: {list(working.keys())}")

                if len(matched_profiles) > 1:
                    # Apply subset resolution
                    sets = [set(extract_name(x) for x in grp) for grp in matched_profiles]
                    non_subset = []
                    for i, s1 in enumerate(sets):
                        if not any(i != j and s1 < s2 for j, s2 in enumerate(sets)):
                            non_subset.append(matched_profiles[i])
                    if len(non_subset) == 1:
                        pass  # resolved
                    else:
                        raise Exception("Ambiguous exclusive profile match")

            return func(*args,**kwargs)
        return wrapper
    return decorator
