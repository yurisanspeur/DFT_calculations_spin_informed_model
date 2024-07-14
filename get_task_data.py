from mp_api.client import MPRester
import numpy as np
import pandas as pd
from pymatgen.analysis.magnetism.analyzer import (
    CollinearMagneticStructureAnalyzer,
    MagneticStructureEnumerator,
    Ordering,
)
import os
from pymatgen.io.vasp.inputs import Potcar, Incar, Kpoints

data_dict = {}  # This will be a nested key whose root key is the composition
df = pd.read_excel("Unique_Structures_Wenbin_magmom.xlsx")
with MPRester(
    api_key="LbNxZC04OmYYQCyDZggQRaRmUjeuM2pF",
) as mpr:
    for index, task_id in enumerate(df["mp_id"].values):
        # task_id = "mp-1232518"
        # First we get the canonical ID from the task id
        mp_id = mpr.get_material_id_from_task_id(str(task_id))
        if index > 0:
            os.chdir("../")
        print(mp_id, task_id)
        # Then we use this master id to retrieve all the underlying tasks
        # task_ids = [
        #    x
        #    for x in mpr.get_task_ids_associated_with_material_id(f"{mp_id}")
        #    if "123" in x
        # ]  # 123 is the tasks associated with magnetic ordering enumeration
        task_docs = mpr.materials.tasks.search(task_id)
        for index, task_doc in enumerate(task_docs):
            if index > 0:
                os.chdir("../")
            os.makedirs(f"{mp_id}-{task_id}", exist_ok=True)
            os.chdir(f"{mp_id}-{task_id}")
            # Write INCAR, POSCAR, KPOINTS and POTCAR
            old_incar_dict = task_doc.calcs_reversed[0].input.incar

            # Let us check whether this material has Gd or Eu
            if 'Gd' in [x.symbol for x in task_doc.calcs_reversed[0].input.structure.species]:
                # Now we get the mask for where these ions are in the structure and will use those to upate the initial guess
                index = np.where(np.array([x.symbol for x in task_doc.calcs_reversed[0].input.structure.species]) == 'Gd')
                orig_magmom_IG = np.array(old_incar_dict['MAGMOM'])
                orig_magmom_IG[index] = 1.3
                old_incar_dict.update({"MAGMOM": orig_magmom_IG.tolist()}) # Update the initial guess
                #breakpoint()
            if 'Eu' in [x.symbol for x in task_doc.calcs_reversed[0].input.structure.species]:
                # Now we get the mask for where these ions are in the structure and will use those to upate the initial guess
                index = np.where(np.array([x.symbol for x in task_doc.calcs_reversed[0].input.structure.species]) == 'Eu')
                orig_magmom_IG = np.array(old_incar_dict['MAGMOM'])
                orig_magmom_IG[index] = 1.3
                old_incar_dict.update({"MAGMOM": orig_magmom_IG.tolist()}) # Update the initial guess
               # breakpoint()
            old_incar_dict.update({"NELM": 1000, "LORBIT": 11})
            Incar.from_dict(old_incar_dict).write_file("INCAR")
            task_doc.calcs_reversed[0].input.kpoints.write_file("KPOINTS")
            task_doc.calcs_reversed[0].input.structure.to(filename="POSCAR")
            try:
                Potcar(symbols=task_doc.calcs_reversed[0].input.potcar).write_file(
                    "POTCAR"
                )
            except OSError:
                print(f"Error for folder {mp_id}-{task_id}")
                continue
            # Let us decorate the pymatgen structures with the magmom and let the CollinearMagneticStructureAnalyzer tag it with an ordering
            # magmoms = task_doc.calcs_reversed[0].input.parameters["MAGMOM"]
            # structure = task_doc.calcs_reversed[0].output.structure
            # structure.add_site_property("magmom", magmoms)
            # analyzer = CollinearMagneticStructureAnalyzer(structure)
            # ordering = analyzer.ordering.value
            # breakpoint()
            # print(
            #    structure.composition,
            #    "input_magmom",
            #    task_doc.calcs_reversed[0].input.parameters["MAGMOM"],
            #    "output_magmom",
            #    [
            #        x["tot"]
            #        for x in task_doc.calcs_reversed[0].output.outcar["magnetization"]
            #    ],
            #    task_doc.calcs_reversed[0].output.energy_per_atom,
            #    ordering,
            # )
            # if structure.composition not in data_dict:
            #    data_dict[structure.composition] = {"FM":{}, "AFM":{},"NM":{}, "FiM":{}}
            # else:
            #    data_dict[]

        # breakpoint()

    # breakpoint()
    # mpr.get_material_id_from_task_id()
