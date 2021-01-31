from odoo import api, fields, models, _


class PinkingListReport(models.AbstractModel):
    _name = 'report.changes_delivery_order.report_picking_list'

    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('changes_delivery_order.report_picking_list')
        deliverys = self.env['stock.picking'].search([('id', 'in', docids)])
        unique_uom = {}
        for delivery in deliverys:
            for line in delivery.move_lines:
                if line.product_uom.name not in unique_uom.keys():
                    unique_uom[line.product_uom.name] = line.product_uom_qty
                else:
                    unique_uom[line.product_uom.name] += line.product_uom_qty

        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': deliverys,
            'unique_uom': unique_uom,
        }
