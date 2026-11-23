"""Independent checks for new beam/column displacement presentations."""
import unittest
from column_flexure import profile

MODEL = {
 "dimensions":{"height":3.0,"column":0.30},
 "column_elastic_modulus_kN_m2":25_000_000,
 "actions":{"column_moment_base":3.3003802281308583,
            "column_moment_roof":6.600760456261717,
            "column_shear":3.3003802281308583}
}

class ColumnBendingTests(unittest.TestCase):
 def test_fixed_base_non_sway_and_peak(self):
  p=profile(MODEL)
  self.assertEqual(len(p["samples"]),61)
  self.assertAlmostEqual(p["samples"][0]["relative_flexure_mm"],0,places=9)
  self.assertAlmostEqual(p["samples"][-1]["relative_flexure_mm"],0,places=9)
  self.assertAlmostEqual(p["peak_z_m"],2.0,places=8)
  self.assertAlmostEqual(p["peak_chord_relative_mm"],-0.1303853917,places=8)
  self.assertAlmostEqual(p["roof_rotation_rad"],0.0002933671314,places=11)
  self.assertEqual(p["roof_translation_mm"],0.0)
 def test_independent_curvature_integral(self):
  p=profile(MODEL)
  EI=p["EI_kN_m2"];m=MODEL["actions"]["column_moment_base"];v=MODEL["actions"]["column_shear"]
  # Weighted integration u(z) = integral_0^z (z-s) M(s)/EI ds
  for z in (0.5,1.0,2.0,2.5):
   n=10000;step=z/n
   displacement=sum((z-(i+.5)*step)*(-m+v*(i+.5)*step)*step/EI for i in range(n))*1000
   exact=next(x["relative_flexure_mm"] for x in p["samples"] if abs(x["z_m"]-z)<1e-10)
   self.assertAlmostEqual(displacement, exact, places=7)
 def test_rejects_inconsistent_shear(self):
  altered={**MODEL,"actions":dict(MODEL["actions"],column_shear=0)}
  with self.assertRaises(ValueError):profile(altered)

if __name__=="__main__":unittest.main()
