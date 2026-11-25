import unittest
from publication_canary import Blocked, Plan, Snapshot, simulate


class CanaryTests(unittest.TestCase):
    def setUp(self):
        self.plan = Plan("test-1", "a" * 40, "b" * 40, "c" * 40, "1")
        self.digest = self.plan.marker_digest
        self.owned = Snapshot(self.digest, ((self.digest, True, True, True),))

    def verify(self, result, status, pushes=0, prs=0):
        self.assertEqual(result["status"], status)
        self.assertFalse(result["readiness_eligible"])
        self.assertTrue(result["simulation"])
        self.assertEqual(result["counts"], dict(fake_push=pushes, fake_pr=prs,
            model_calls=0, real_external_effects=0, cleanup=0, merge=0))

    def test_fresh_and_replay(self):
        r = simulate(self.plan)
        self.verify(r, "simulated-draft-verified", 1, 1)
        self.verify(simulate(self.plan, r["snapshot"]), "verified-reuse")

    def test_resume_owned_branch(self):
        self.verify(simulate(self.plan, Snapshot(self.digest)), "simulated-draft-verified", 0, 1)

    def test_denied_pr(self):
        self.verify(simulate(self.plan, pr_outcome="denied"), "blocked", 1, 1)

    def test_ambiguous_pr_no_retry(self):
        self.verify(simulate(self.plan, pr_outcome="ambiguous"), "blocked", 1, 1)
        self.verify(simulate(self.plan, pr_outcome="ambiguous", ambiguous_snapshot=self.owned),
                    "simulated-draft-verified", 1, 1)

    def test_unreadable_or_conflicting(self):
        for s in (Snapshot(readable=False), Snapshot("foreign"),
                  Snapshot(self.digest, self.owned.prs * 2),
                  Snapshot(self.digest, ((self.digest, True, False, True),)),
                  Snapshot(self.digest, ((self.digest, False, True, True),)),
                  Snapshot(self.digest, ((self.digest, True, True, False),)),
                  Snapshot(None, self.owned.prs)):
            with self.subTest(snapshot=s):
                self.verify(simulate(self.plan, s), "blocked")

    def test_permission_and_dry_run(self):
        self.verify(simulate(self.plan, permission=False), "blocked")
        self.verify(simulate(self.plan, dry_run=False), "blocked")

    def test_push_uncertain(self):
        self.verify(simulate(self.plan, push_outcome="ambiguous"), "blocked", 1, 0)

    def test_binding_drift(self):
        for p in (Plan("test-1", "d" * 40, "b" * 40, "c" * 40, "1"),
                  Plan("test-1", "a" * 40, "d" * 40, "c" * 40, "1"),
                  Plan("test-1", "a" * 40, "b" * 40, "d" * 40, "1"),
                  Plan("test-1", "a" * 40, "b" * 40, "c" * 40, "2")):
            self.verify(simulate(p, self.owned), "blocked")

    def test_invalid_plan(self):
        with self.assertRaises(Blocked):
            Plan("../invalid", "a" * 40, "b" * 40, "c" * 40, "1")
        with self.assertRaises(Blocked):
            Plan("test-1", "main", "b" * 40, "c" * 40, "1")


if __name__ == "__main__":
    unittest.main()
