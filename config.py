from pathlib import Path

experiment_path = Path('/ceph/aeon/aeon/data/raw/AEONX1/manual_ProbeSurvey/ProbeSurvey1_M42')

epoch_name_to_shank = {
    '2026-10-20T100636Z': 's1bot',
    '2026-10-20T101200Z': 's1top',
    '2026-10-20T101721Z': 's2bot',
    '2026-10-20T102243Z': 's2top',
    '2026-10-20T102820Z': 's3bot',
    '2026-10-20T103329Z': 's3top',
    '2026-10-20T103839Z': 's4bot',
    '2026-10-20T104352Z': 's4top',
}

probe_names = ['ProbeA', 'ProbeB']
