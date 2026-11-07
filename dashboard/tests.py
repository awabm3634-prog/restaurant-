    def test_manager_sees_only_own_branch_staff(self):
        r = self.get("dashboard:staff_list", self.mgr_a, branch_id=self.a.id)
        self.assertEqual(r.status_code, 200)
        usernames = [m.user.username for m in r.context["staff"]]
        self.assertIn("mgr_a", usernames)
        self.assertNotIn("mgr_b", usernames)

    def test_manager_cannot_open_other_branch_staff_list(self):
        r = self.get("dashboard:staff_list", self.mgr_a, branch_id=self.b.id)
        self.assertEqual(r.status_code, 403)

    def test_cashier_cannot_open_staff_list(self):
        cashier = self._staff("cash_a", self.a, role=Role.CASHIER)
        r = self.get("dashboard:staff_list", cashier, branch_id=self.a.id)
        self.assertEqual(r.status_code, 403)
