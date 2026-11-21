import copy, json, math, sys, unittest
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import build_public
from engine import PARAMETERS,compute,digest,make_schedule,parse_rows,mdm

class ExperimentTests(unittest.TestCase):
    def setUp(self): self.p={k:v for k,v,u,n in PARAMETERS}
    def test_shared_quantities_and_load_path(self):
        r=compute(self.p)
        self.assertEqual(len(r['columns']),4); self.assertEqual(len(r['beams']),4)
        self.assertAlmostEqual(r['concrete_m3'],4.59)
        self.assertAlmostEqual(r['analysis']['total_load_kN'],162.75)
        self.assertAlmostEqual(r['analysis']['base_reaction_each_kN'],40.6875)
        self.assertAlmostEqual(r['concrete_subtotal_npr'],55080)
        self.assertIsNone(r['excluded']['steel_quantity_kg'])
    def test_mdm_against_independent_slope_deflection(self):
        for kb in (.0003,.002,.005):
            for L in (3,4,6):
                m=mdm(L,3,25e6,kb,.000675,20)
                self.assertLess(m['joint_residual_kNm'],1e-9)
                self.assertAlmostEqual(abs(m['beam_I_kNm']),m['independent_hogging_kNm'],places=8)
    def test_rectangle_and_zero_superimposed_load(self):
        self.p.update(span_x=5,span_y=3,finish_load=0,live_load=0)
        r=compute(self.p)
        self.assertAlmostEqual(2*sum(r['analysis'][x]['tributary_area_m2'] for x in ('x','y')),15)
        self.assertAlmostEqual(r['analysis']['total_load_kN'],r['concrete_m3']*25)
    def test_one_input_changes_every_workflow(self):
        a=make_schedule(self.p,compute(self.p)); bparams={**self.p,'span_x':5}; b=make_schedule(bparams,compute(bparams))
        self.assertNotEqual(a['slab']['area_m2'],b['slab']['area_m2'])
        self.assertNotEqual(a['analysis']['x']['beam_I_kNm'],b['analysis']['x']['beam_I_kNm'])
        self.assertNotEqual(a['concrete_subtotal_npr'],b['concrete_subtotal_npr'])
        self.assertNotEqual(a['schedule']['finish_date'],b['schedule']['finish_date'])
    def test_calendar_curing_and_saturday(self):
        self.p['start_date']='2026-11-21' # Saturday
        r=make_schedule(self.p,compute(self.p))
        for a in r['schedule']['activities']:
            start=date.fromisoformat(a['start']);end=date.fromisoformat(a['finish'])
            if a['duration_basis']=='work':
                self.assertNotEqual(start.weekday(),5);self.assertNotEqual(end.weekday(),5)
            else: self.assertEqual((end-start).days+1,a['active_duration'])
    def test_input_integrity_and_invalid_geometry(self):
        rows=[['Parameter','Value','Unit','Basis']]+[[k,v,u,n] for k,v,u,n in PARAMETERS]
        self.assertEqual(parse_rows(rows),self.p)
        with self.assertRaises(ValueError):parse_rows(rows+[rows[1]])
        changed=copy.deepcopy(rows);changed[1][2]='ft'
        with self.assertRaises(ValueError):parse_rows(changed)
        for bad in [None,0,float('nan'),True]:
            with self.assertRaises(ValueError):compute({**self.p,'span_x':bad})
        with self.assertRaises(ValueError):compute({**self.p,'beam_depth':.1})

    def test_public_build_keeps_inactive_inputs_and_raw_hashes_out_of_artifacts(self):
        inactive = dict(steel_rate=98765, formwork_rate=87654, latitude=1.23456, longitude=-2.34567)
        parameters = {**self.p, **inactive, 'span_x': 5}
        public_inputs = {**self.p, 'span_x': 5}
        for key in inactive:
            del public_inputs[key]
        raw_hashes = dict(input_sha256=digest(parameters), sheet_export_sha256='a'*64,
                          academic_export_sha256='b'*64, academic_sha256='c'*64)
        provenance = {**raw_hashes, 'source_mode': 'google_link_read_exports',
                      'read_at': '2026-01-01T00:00:00+00:00', 'source_payload_repeat_check': True}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / 'source-snapshot.json'
            snapshot.write_text(json.dumps(dict(parameters=parameters, provenance=provenance)))
            (root / 'peer-methods.json').write_text((build_public.ROOT / 'peer-methods.json').read_text())
            out = root / 'public'
            with patch.object(build_public, 'ROOT', root):
                build_public.build(out)
            self.assertEqual(json.loads(snapshot.read_text())['parameters'], parameters)
            published = json.loads((out / 'results.json').read_text())
            self.assertEqual(published['parameters'], public_inputs)
            self.assertEqual(published['input_sha256'], digest(public_inputs))
            self.assertEqual(published['provenance']['public_input_sha256'], digest(public_inputs))
            self.assertEqual(published['provenance']['read_at'], provenance['read_at'])
            self.assertEqual(published['slab']['area_m2'], 20)
            self.assertTrue(published['schedule']['activities'])
            self.assertGreater(published['concrete_subtotal_npr'], 55080)
            for artifact in out.iterdir():
                for fingerprint in raw_hashes.values():
                    self.assertNotIn(fingerprint, artifact.read_text())

if __name__=='__main__':unittest.main()
