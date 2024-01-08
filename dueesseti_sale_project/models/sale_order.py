from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line.product_id", "order_line.project_id")
    def _compute_project_ids(self):
        super()._compute_project_ids()

        for order in self:
            order.project_ids |= self.env["project.project"].search(
                ["|", ("sale_line_id", "in", order.order_line.ids), ("sale_order_id", "=", order.id)]
            )
