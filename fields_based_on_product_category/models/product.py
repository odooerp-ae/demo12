# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from odoo.osv.orm import setup_modifiers
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False,
                        submenu=False):

        default_categ_id = self.env.context.get('default_categ_id')
        active_id = self.env.context.get('params')
        res = super(ProductTemplate, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            submenu=submenu
        )
        if default_categ_id and view_type == 'form':
            controls_dict = {
                'show_dimensions_length': 'dimensions_length',
                'show_dimensions_width': 'dimensions_width',
                'show_dimensions_height': 'dimensions_height',
                'show_dimensions_diamter': 'dimensions_diamter',
                'show_artwork': 'artwork',
                'show_code': 'code',
                'show_brand': 'brand',
                'show_top_type': 'top_type',
                'show_sae': 'sae',
                'show_api': 'api',
                'show_weight': 'categ_weight',
                'show_thickness': 'thickness',
                'show_background_color': 'background_color',
                'show_no_plyes': 'no_plyes',
                'show_pressing_type': 'pressing_type',
                'show_material': 'material',
                'show_shape': 'shape',
                'show_mold': 'mold',
                'show_bottom_color': 'bottom_color',
                'show_cover_color': 'cover_color',
                'show_top_color': 'top_color',
                'show_color': 'color',
                'show_ribbon_color': 'ribbon_color',
                'show_logo_color': 'logo_color',
                'show_logo_location': 'logo_location',
                'show_closure_type': 'closure_type',
                'show_marking_options': 'marking_options',
                'show_picture_rightside': 'picture_rightside',
                'show_picture_leftside': 'picture_leftside',
                'show_picture_front': 'picture_front',
                'show_picture_angle': 'picture_angle',
                'show_picture': 'picture',
                'show_picture_top': 'picture_top',
                'show_picture_side1': 'picture_side1',
                'show_picture_side2': 'picture_side2',
                'show_label_dimensions_width': 'label_dimensions_width',
                'show_label_dimensions_height': 'label_dimensions_height',
                'show_printed_can': 'printed_can',
                'show_no_impressions_front': 'no_impressions_front',
                'show_no_impressions_back': 'no_impressions_back',
                'show_print_artork_pdf': 'print_artork_pdf',
                'show_notes': 'notes',
                'show_language': 'language',
                'show_status': 'status',
                'show_no_rings': 'no_rings',

            }
            res = self.invisible_product_control(default_categ_id, controls_dict, res)
        return res

    def invisible_product_control(self, default_categ_id, controls_dict, res):
        for key, value in controls_dict.items():
            filter_by = self.env['product.category'].browse(default_categ_id).mapped(str(key))[0]
            doc = etree.XML(res['arch'])
            if not filter_by:
                path = "//field[@name='" + str(value) + "']"
                for node in doc.xpath(str(path)):
                    node.set('invisible', '1')
                    setup_modifiers(node, res['fields'][str(value)])

                    res['arch'] = etree.tostring(doc)
        return res

    weight = fields.Float(
        string='Gross Weight', compute='_compute_weight', digits=dp.get_precision('Stock Weight'),
        inverse='_set_weight', store=True,
        help="The weight of the contents in Kg, not including any packaging, etc.")
    dimensions_length = fields.Float(string='Dimensions Length')
    dimensions_width = fields.Float(string='Dimensions Width')
    dimensions_height = fields.Float(string='Dimensions Height')
    dimensions_diamter = fields.Float(string='Dimensions Diamter')
    artwork = fields.Binary(string='Artwork')
    code = fields.Char(string='Code')
    brand = fields.Char(string='Brand')
    top_type = fields.Char(string=' Top Type')
    sae = fields.Char(string='SAE')
    api = fields.Char(string='API')
    pressing_type = fields.Char(string='Pressing Type')
    background_color = fields.Char(string='Background Color')
    no_plyes = fields.Integer(string='Number of Plyes')
    categ_weight = fields.Float(string='weight')
    thickness = fields.Float(string='Thickness')
    material = fields.Char(string='Material')
    shape = fields.Char(string='Shape')
    mold = fields.Char(string='Mold')
    bottom_color = fields.Char(string='Bottom Color')
    cover_color = fields.Char(string='Cover Color')
    top_color = fields.Char(string='Top color')
    color = fields.Char(string='color')
    ribbon_color = fields.Char(string='Ribbon color')
    logo_color = fields.Char(string='logo color')
    logo_location = fields.Char(string='logo Location')
    closure_type = fields.Char(string='Closure Type')
    marking_options = fields.Char(string='Marking Options')
    picture_rightside = fields.Binary(string='Picture Rightside')
    picture_leftside = fields.Binary(string='Picture Leftside')
    picture_front = fields.Binary(string='Picture Front')
    picture_angle = fields.Binary(string='Picture Angle')
    picture = fields.Binary(string='Picture')
    picture_top = fields.Binary(string='Picture Top')
    picture_side1 = fields.Binary(string='Picture Side1')
    picture_side2 = fields.Binary(string='Picture side2')
    label_dimensions_width = fields.Float(string='Label Dimensions Width')
    label_dimensions_height = fields.Float(string='Label Dimensions Height')
    printed_can = fields.Char(string='Printed Can')
    no_impressions_front = fields.Char(string='Number of impressions_front')
    no_impressions_back = fields.Char(string='Number of impressions_back')
    print_artork_pdf = fields.Char(string='Print Artwork PDF')
    notes = fields.Char(string='Notes')
    language = fields.Char(string='language')
    status = fields.Char(string='status')
    no_rings = fields.Char(string='Number of rings')

    show_dimensions_length = fields.Boolean(related='categ_id.show_dimensions_length',
                                            string='Show Dimensions Length')
    show_dimensions_width = fields.Boolean(related='categ_id.show_dimensions_width',
                                           string='Show Dimensions Width')
    show_dimensions_height = fields.Boolean(related='categ_id.show_dimensions_height',
                                            string='Show Dimensions Height')
    show_dimensions_diamter = fields.Boolean(related='categ_id.show_dimensions_diamter',
                                             string='Show Dimensions Diamter')
    show_artwork = fields.Boolean(related='categ_id.show_artwork', string='Show artwork')
    show_code = fields.Boolean(related='categ_id.show_code', string='Show code')
    show_brand = fields.Boolean(related='categ_id.show_brand', string='Show Brand')
    show_top_type = fields.Boolean(related='categ_id.show_top_type', string='Show Top Type')
    show_sae = fields.Boolean(related='categ_id.show_sae', string='Show SAE')
    show_api = fields.Boolean(related='categ_id.show_api', string='Show API')
    show_pressing_type = fields.Boolean(related='categ_id.show_pressing_type',
                                        string='Show Pressing Type')
    show_background_color = fields.Boolean(related='categ_id.show_background_color',
                                           string='Show Background Color')
    show_no_plyes = fields.Boolean(related='categ_id.show_no_plyes', string='Show Number of Plyes')
    show_weight = fields.Boolean(related='categ_id.show_weight', string='Show weight')
    show_thickness = fields.Boolean(related='categ_id.show_thickness', string='Show thickness')
    show_material = fields.Boolean(related='categ_id.show_material', string='Show Material')
    show_shape = fields.Boolean(related='categ_id.show_shape', string='Show Shape')
    show_mold = fields.Boolean(related='categ_id.show_mold', string='Show Mold')
    show_bottom_color = fields.Boolean(related='categ_id.show_bottom_color',
                                       string='Show Bottom Color')
    show_cover_color = fields.Boolean(related='categ_id.show_cover_color',
                                      string='Show Cover Color')
    show_top_color = fields.Boolean(related='categ_id.show_top_color', string='Show Top color')
    show_color = fields.Boolean(related='categ_id.show_color', string='Show color')
    show_ribbon_color = fields.Boolean(related='categ_id.show_ribbon_color',
                                       string='Show Ribbon color')
    show_logo_color = fields.Boolean(related='categ_id.show_logo_color', string='Show logo color')
    show_logo_location = fields.Boolean(related='categ_id.show_logo_location',
                                        string='Show logo Location')
    show_closure_type = fields.Boolean(related='categ_id.show_closure_type',
                                       string='Show Closure Type')
    show_marking_options = fields.Boolean(related='categ_id.show_marking_options',
                                          string='Show Marking Options')
    show_picture_rightside = fields.Boolean(related='categ_id.show_picture_rightside',
                                            string='Show Picture Rightside')
    show_picture_leftside = fields.Boolean(related='categ_id.show_picture_leftside',
                                           string='Show Picture Leftside')
    show_picture_front = fields.Boolean(related='categ_id.show_picture_front',
                                        string='Show Picture Front')
    show_picture_angle = fields.Boolean(related='categ_id.show_picture_angle',
                                        string='Show Picture Angle')
    show_picture = fields.Boolean(related='categ_id.show_picture', string='Show Picture')
    show_picture_top = fields.Boolean(related='categ_id.show_picture_top',
                                      string='Show Picture Top')
    show_picture_side1 = fields.Boolean(related='categ_id.show_picture_side1',
                                        string='Show Picture Side1')
    show_picture_side2 = fields.Boolean(related='categ_id.show_picture_side2',
                                        string='Show Picture side2')
    show_label_dimensions_width = fields.Boolean(related='categ_id.show_label_dimensions_width',
                                                 string='Show Label Dimensions Width')
    show_label_dimensions_height = fields.Boolean(related='categ_id.show_label_dimensions_height',
                                                  string='Show Label Dimensions Height')
    show_printed_can = fields.Boolean(related='categ_id.show_printed_can',
                                      string='Show Printed Can')
    show_no_impressions_front = fields.Boolean(related='categ_id.show_no_impressions_front',
                                               string='Show Number of impressions_front')
    show_no_impressions_back = fields.Boolean(related='categ_id.show_no_impressions_back',
                                              string='Show Number of impressions_back')
    show_print_artork_pdf = fields.Boolean(related='categ_id.show_print_artork_pdf',
                                           string='Show Print Artwork PDF')
    show_notes = fields.Boolean(related='categ_id.show_notes', string='Show Notes')
    show_language = fields.Boolean(related='categ_id.show_language', string='Show language')
    show_status = fields.Boolean(related='categ_id.show_status', string='Show status')
    show_no_rings = fields.Boolean(related='categ_id.show_no_rings', string='Show Number of rings')
