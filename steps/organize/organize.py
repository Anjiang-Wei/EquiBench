from dataclasses import dataclass, field
import json
import logging
from pathlib import Path

from natsort import natsorted

from type             import Category, Problem, Pair, DCEName, InfoDictKey, OJName, STOKEName, TVEName


    
def problems_from_organize(category: Category, organize_path: Path, with_content: bool):
    names = [subpath.name for subpath in organize_path.iterdir() if subpath.is_dir()]
    n = len(names)
    names = natsorted(names)

    problems, pair_index = list[Problem](), 0
    for problem_index in range(n):
        problem, pair_index = problem_from_organize(category=category, organize_path=organize_path, names=names, problem_index=problem_index, start_pair_index=pair_index)
        if with_content:
            problem = problem.with_content()
        problems.append(problem)

    logging.info(f"[Category: {category.value: <6}][Problem] Load {len(problems)} problems.")
    return problems

def problem_from_organize(category: Category, organize_path: Path, names: list[str], problem_index: int, start_pair_index: int) -> tuple[Problem, int]:
    name = names[problem_index]
    problem_path = organize_path / name
    n = len(names)
    match category:
        case Category.DCE:

            target_c_path = problem_path / DCEName.TARGET_C.value
            eq_c_path     = problem_path / DCEName    .EQ_C.value
            neq_c_path    = problem_path / DCEName   .NEQ_C.value

            pairs = [
                Pair(
                    pair_id          = start_pair_index,
                    program_1_path   = target_c_path, 
                    program_2_path   = eq_c_path, 
                    truth_label      = True,

                    category = category,
                    problem_id       = problem_index,
                    problem_path     = problem_path
                ),
                Pair(
                    pair_id          = start_pair_index + 1,
                    program_1_path   = target_c_path, 
                    program_2_path   = neq_c_path, 
                    truth_label      = False,

                    category = category,
                    problem_id       = problem_index,
                    problem_path     = problem_path
                )
            ]
            return Problem(
                category   = category,
                problem_id         = problem_index, 
                path       = problem_path,

                pairs      =  pairs
            ), start_pair_index + 2
        case Category.TVM:
            problem_1_path = problem_path
            problem_2_path = organize_path / names[(problem_index + 1) % n]

            problem_1_program_paths = natsorted(problem_1_path.glob(TVEName.WILDCARD.value))
            problem_2_program_paths = natsorted(problem_2_path.glob(TVEName.WILDCARD.value))

            assert len(problem_1_program_paths) == 2, f"{problem_1_program_paths} does not contain exactly 2 .cu files."
            assert len(problem_2_program_paths) == 2, f"{problem_2_program_paths} does not contain exactly 2 .cu files."
                
            program_1_1_cu_path = problem_1_program_paths[0]
            program_1_2_cu_path = problem_1_program_paths[1]
            program_2_1_cu_path = problem_2_program_paths[0]

            pairs = [
                Pair(
                    pair_id          = start_pair_index,
                    program_1_path   = program_1_1_cu_path, 
                    program_2_path   = program_1_2_cu_path, 
                    truth_label      = True,

                    category = category,
                    problem_id       = problem_index,
                    problem_path     = problem_path
                ),
                Pair(
                    pair_id          = start_pair_index + 1,
                    program_1_path   = program_1_1_cu_path, 
                    program_2_path   = program_2_1_cu_path, 
                    truth_label      = False,

                    category = category,
                    problem_id       = problem_index,
                    problem_path     = problem_path
                )
            ]
            return Problem(
                category = category,
                problem_id       = problem_index, 
                path     = problem_path, 
                
                pairs    = pairs
            ), start_pair_index + 2
        case Category.STOKE:
            info_json_path = problem_path / STOKEName.INFO_JSON.value
            target_s_path  = problem_path / STOKEName.TARGET_S.value

            eq_s_paths     = natsorted(problem_path.glob(STOKEName.TEMPLATE.value.format(label=STOKEName.EQ.value, index="*")))
            neq_s_paths    = natsorted(problem_path.glob(STOKEName.TEMPLATE.value.format(label=STOKEName.NEQ.value, index="*")))

            with open(info_json_path, "r") as file:
                info = json.load(file)
            
            info_def_in       = info[InfoDictKey.DEF_IN.value]
            info_live_out     = info[InfoDictKey.LIVE_OUT.value]

            # pairs
            eq_pairs  = [Pair(
                pair_id          = start_pair_index + index,
                program_1_path   = target_s_path, 
                program_2_path   = path, 
                truth_label      = True, 

                category = category,
                problem_id       = problem_index,
                problem_path     = problem_path,
                problem_def_in   = info_def_in, 
                problem_live_out = info_live_out,
            ) for index, path in enumerate(eq_s_paths)]

            neq_pairs = [Pair(
                pair_id          = start_pair_index + len(eq_pairs) + index,
                program_1_path   = target_s_path, 
                program_2_path   = path, 
                truth_label      = False, 
                
                category = category,
                problem_id       = problem_index,
                problem_path     = problem_path,
                problem_def_in   = info_def_in, 
                problem_live_out = info_live_out
            ) for index, path in enumerate(neq_s_paths)]

            pairs = eq_pairs + neq_pairs

            assert pairs

            return Problem(
                category = category,
                problem_id       = problem_index, 
                path     = problem_path, 
                
                pairs    = pairs,

                def_in   = info_def_in,
                live_out = info_live_out
            ), start_pair_index + len(pairs)
        case Category.OJ_V:
            accepted_paths         = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.ACCEPTED      .value, index="*")))
            obfused_accepted_paths = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.OBFUS_ACCEPTED.value, index="*")))
            obfused_wrong_paths    = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.OBFUS_WRONG   .value, index="*")))
            problem_html_path      = problem_path / OJName.PROBLEM_HTML.value
            pairs = [
                Pair(
                    pair_id           = start_pair_index,
                    program_1_path    = accepted_paths        [0], 
                    program_2_path    = obfused_accepted_paths[0], 
                    truth_label       = True,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                ),
                Pair(
                    pair_id           = start_pair_index + 1,
                    program_1_path    = accepted_paths     [0], 
                    program_2_path    = obfused_wrong_paths[0], 
                    truth_label       = False,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                )
            ]
            return Problem(
                category   = category,
                problem_id = problem_index, 
                path       = problem_path, 
                
                pairs      = pairs,
                html_path  = problem_html_path
            ), start_pair_index + 2
        case Category.OJ_A:
            accepted_paths    = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.ACCEPTED.value, index="*")))
            wrong_paths       = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.WRONG   .value, index="*")))
            problem_html_path = problem_path / OJName.PROBLEM_HTML.value

            pairs = [
                Pair(
                    pair_id           = start_pair_index,
                    program_1_path    = accepted_paths[0], 
                    program_2_path    = accepted_paths[1], 
                    truth_label       = True,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                ),
                Pair(
                    pair_id          = start_pair_index + 1,
                    program_1_path   = accepted_paths[0], 
                    program_2_path   = wrong_paths   [0], 
                    truth_label      = False,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                )
            ]
            return Problem(
                category   = category,
                problem_id = problem_index, 
                path       = problem_path, 
                
                pairs      = pairs,
                html_path  = problem_html_path
            ), start_pair_index + 2
        case Category.OJ_VA:
            obfused_accepted_paths = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.OBFUS_ACCEPTED.value, index="*")))
            obfused_wrong_paths    = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.OBFUS_WRONG   .value, index="*")))
            problem_html_path      = problem_path / OJName.PROBLEM_HTML.value

            pairs = [
                Pair(
                    pair_id           = start_pair_index,
                    program_1_path    = obfused_accepted_paths[0], 
                    program_2_path    = obfused_accepted_paths[1], 
                    truth_label       = True,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                ),
                Pair(
                    pair_id           = start_pair_index + 1,
                    program_1_path    = obfused_accepted_paths[0], 
                    program_2_path    = obfused_wrong_paths   [0], 
                    truth_label       = False,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                )
            ]
            return Problem(
                category   = category,
                problem_id = problem_index, 
                path       = problem_path, 
                
                pairs      = pairs,
                html_path  = problem_html_path
            ), start_pair_index + 2
        case Category.OJ:
            accepted_paths         = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.ACCEPTED      .value, index="*")))
            wrong_paths            = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.WRONG         .value, index="*")))
            obfused_accepted_paths = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.OBFUS_ACCEPTED.value, index="*")))
            obfused_wrong_paths    = natsorted(problem_path.glob(OJName.TEMPLATE.value.format(label=OJName.OBFUS_WRONG   .value, index="*")))
            problem_html_path      = problem_path / OJName.PROBLEM_HTML.value

            pairs = [
                Pair(
                    pair_id           = start_pair_index,
                    program_1_path    = accepted_paths[0], 
                    program_2_path    = accepted_paths[1], 
                    truth_label       = True,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                ),
                Pair(
                    pair_id           = start_pair_index + 1,
                    program_1_path    = wrong_paths[0], 
                    program_2_path    = wrong_paths[1], 
                    truth_label       = False,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                ),
                Pair(
                    pair_id           = start_pair_index + 2,
                    program_1_path    = obfused_accepted_paths[0], 
                    program_2_path    = obfused_accepted_paths[1], 
                    truth_label       = True,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                ),
                Pair(
                    pair_id          = start_pair_index + 3,
                    program_1_path   = obfused_wrong_paths[0], 
                    program_2_path   = obfused_wrong_paths[1], 
                    truth_label      = False,

                    category          = category,
                    problem_id        = problem_index,
                    problem_path      = problem_path,
                    problem_html_path = problem_html_path
                )

            ]
            return Problem(
                category   = category,
                problem_id = problem_index, 
                path       = problem_path, 
                
                pairs      = pairs,
                html_path  = problem_html_path
            ), start_pair_index + 4
