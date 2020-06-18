from gettsim.config import INTERNAL_FUNCTION_FILES
from gettsim.config import ROOT_DIR
from gettsim.functions_loader import load_functions


def test_funcs_in_doc_module_and_func_from_internal_files_are_the_same():
    documented_functions = load_functions(
        ROOT_DIR / "functions.py", allow_imported_members=True
    )

    internal_function_files = [ROOT_DIR.joinpath(p) for p in INTERNAL_FUNCTION_FILES]
    internal_functions = load_functions(
        internal_function_files, allow_imported_members=True
    )

    # Fix because private functions are not imported in functions.py. Remove when all
    # functions in the DAG became public.
    internal_functions = {
        k: v for k, v in internal_functions.items() if not k.startswith("_")
    }

    assert set(documented_functions) == set(internal_functions)
