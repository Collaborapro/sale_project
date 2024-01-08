from odoo import _
from odoo.addons.sale_project.models.sale_order_line import SaleOrderLine


def _timesheet_create_project(self):
    self.ensure_one()

    projects = []

    for counter in range(int(self.product_uom_qty)):
        values = self._timesheet_create_project_prepare_values()

        if self.product_id.project_template_id:
            values["name"] = f"{values.get('name')} - {self.product_id.project_template_id.name}"
            project = self.product_id.project_template_id.with_context(no_create_folder=True).copy(values)
            project.tasks.write({
                "sale_line_id": self.id,
                "partner_id": self.order_id.partner_id.id,
                "email_from": self.order_id.partner_id.email,
            })
            project.tasks.filtered("parent_id").write({
                "sale_line_id": self.id,
                "sale_order_id": self.order_id.id
            })

        else:
            project_only_sol_count = self.env["sale.order.line"].search_count([
                ("order_id", "=", self.order_id.id),
                ("product_id.service_tracking", "in", ["project_only", "task_in_project"]),
            ])

            if project_only_sol_count == 1:
                values["name"] = (
                    f"{values.get('name')} - "
                    f"{f'[{self.product_id.default_code}] {self.product_id.name}' if self.product_id.default_code else self.product_id.name}"
                )

            project = self.env["project.project"].with_context(no_create_folder=True).create(values)

        if not project.type_ids:
            project.type_ids = self.env["project.task.type"].create({"name": _("New")})

        projects.append(project)

        if not self.project_id:
            self.write({"project_id": project.id})

    return projects[0]

SaleOrderLine._timesheet_create_project = _timesheet_create_project
