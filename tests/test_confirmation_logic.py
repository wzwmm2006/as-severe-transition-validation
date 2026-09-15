from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cohort.logic import first_confirmations, severe_flags


def exam(offset,key,**values):
    return {"dt":datetime(2020,1,1)+timedelta(days=offset),"study_key":key,"patient_key":"synthetic","age":70,"x":values}


def transition():
    base=exam(-10,"base",ava=1.2,lvef=40); index=exam(0,"index",ava=.9)
    return base,index,severe_flags(index)


def test_followup_window_and_first_evaluable_selection():
    t=transition(); before=exam(29,"before",ava=.8); first=exam(30,"first",ava=1.2); later=exam(50,"later",ava=.8)
    result=first_confirmations({"synthetic":t},{"synthetic":[t[1],before,first,later]})
    assert result["synthetic"][1]["study_key"]=="first"
    assert not any(severe_flags(result["synthetic"][1]).values())


def test_confirmed_and_upper_boundary_included():
    t=transition(); follow=exam(365,"follow",mg=42)
    result=first_confirmations({"synthetic":t},{"synthetic":[t[1],follow]})
    assert any(severe_flags(result["synthetic"][1]).values())


def test_after_upper_boundary_excluded():
    t=transition(); follow=exam(366,"follow",ava=.8)
    assert first_confirmations({"synthetic":t},{"synthetic":[t[1],follow]})=={}


def test_unevaluable_exam_is_skipped():
    t=transition(); missing=exam(40,"missing",lvef=35); evaluable=exam(60,"evaluable",vmax=4.1)
    result=first_confirmations({"synthetic":t},{"synthetic":[t[1],missing,evaluable]})
    assert result["synthetic"][1]["study_key"]=="evaluable"
