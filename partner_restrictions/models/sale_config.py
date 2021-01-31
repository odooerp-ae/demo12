from odoo import api, fields, models
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_ids  = fields.Many2many(comodel_name="res.users", string="Users TO access All partners", )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter']
        x = param_obj.sudo().get_param('op.user_ids')

        lines = False
        print(x)
        if x:
            lines = [[6, 0, x]]
            res.update( {
                'user_ids': lines
            })
        return res
    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('op.user_ids', self.user_ids.ids)
        partners = self.env['res.partner'].search([])
        for partner in partners:
            partner.user_ids=self.user_ids.ids
