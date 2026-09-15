from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cohort.logic import concordant, exclude_prior_valve, first_transitions, severe_flags


def exam(day, key, **values):
    return {"dt": datetime(2020, 1, day), "study_key": key, "patient_key": "synthetic", "age": 70, "x": values}


def test_severe_parameter_patterns():
    assert severe_flags(exam(1,"a",ava=.9)) == {"AVA":True,"Vmax":False,"MG":False}
    assert severe_flags(exam(1,"b",vmax=4.1))["Vmax"]
    assert severe_flags(exam(1,"c",mg=40))["MG"]
    assert concordant(severe_flags(exam(1,"d",ava=.9,vmax=4.1)))
    assert concordant(severe_flags(exam(1,"e",ava=.9,mg=41)))


def test_missing_velocity_and_gradient_are_unavailable():
    assert severe_flags(exam(1,"a",ava=.9)) == {"AVA":True,"Vmax":False,"MG":False}


def test_first_transition_and_deterministic_same_time_ordering():
    baseline=exam(1,"baseline",ava=1.2,lvef=40)
    later=exam(2,"b",ava=.8); first=exam(2,"a",vmax=4.2)
    exams=sorted([baseline,later,first],key=lambda x:(x["dt"],x["study_key"]))
    result=first_transitions({"synthetic":baseline},{"synthetic":exams})
    assert result["synthetic"][1]["study_key"] == "a"


def test_prior_avr_exclusion_but_same_day_is_retained():
    baseline=exam(5,"base",ava=1.2,lvef=40); index=exam(10,"index",ava=.9)
    transitions={"synthetic":(baseline,index,severe_flags(index))}
    prior={"synthetic":[{"dt":datetime(2020,1,4),"class":"SAVR"}]}
    same_day={"synthetic":[{"dt":datetime(2020,1,10),"class":"TAVR"}]}
    assert exclude_prior_valve({"synthetic":baseline},transitions,prior)=={"synthetic"}
    assert exclude_prior_valve({"synthetic":baseline},transitions,same_day)==set()
