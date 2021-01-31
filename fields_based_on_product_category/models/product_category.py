# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree
from odoo.osv.orm import setup_modifiers
from datetime import date, datetime, time, timedelta


class ProductCategory(models.Model):
    _inherit = 'product.category'

    show_dimensions_length = fields.Boolean(default=False, string='Show Dimensions Length')
    show_dimensions_width = fields.Boolean(default=False, string='Show Dimensions Width')
    show_dimensions_height = fields.Boolean(default=False, string='Show Dimensions Height')
    show_dimensions_diamter = fields.Boolean(default=False, string='Show Dimensions Diamter')
    show_artwork = fields.Boolean(default=False, string='Show artwork')
    show_code = fields.Boolean(default=False, string='Show code')
    show_brand = fields.Boolean(default=False, string='Show Brand')
    show_top_type = fields.Boolean(default=False, string='Show Top Type')
    show_sae = fields.Boolean(default=False, string='Show SAE')
    show_api = fields.Boolean(default=False, string='Show API')
    show_pressing_type = fields.Boolean(default=False, string='Show Pressing Type')
    show_background_color = fields.Boolean(default=False, string='Show Background Color')
    show_no_plyes = fields.Boolean(default=False, string='Show Number of Plyes')
    show_weight = fields.Boolean(default=False, string='Show weight')
    show_thickness = fields.Boolean(default=False, string='Show thickness')
    show_material = fields.Boolean(default=False, string='Show Material')
    show_shape = fields.Boolean(default=False, string='Show Shape')
    show_mold = fields.Boolean(default=False, string='Show Mold')
    show_bottom_color = fields.Boolean(default=False, string='Show Bottom Color')
    show_cover_color = fields.Boolean(default=False, string='Show Cover Color')
    show_top_color = fields.Boolean(default=False, string='Show Top color')
    show_color = fields.Boolean(default=False, string='Show color')
    show_ribbon_color = fields.Boolean(default=False, string='Show Ribbon color')
    show_logo_color = fields.Boolean(default=False, string='Show logo color')
    show_logo_location = fields.Boolean(default=False, string='Show logo Location')
    show_closure_type = fields.Boolean(default=False, string='Show Closure Type')
    show_marking_options = fields.Boolean(default=False, string='Show Marking Options')
    show_picture_rightside = fields.Boolean(default=False, string='Show Picture Rightside')
    show_picture_leftside = fields.Boolean(default=False, string='Show Picture Leftside')
    show_picture_front = fields.Boolean(default=False, string='Show Picture Front')
    show_picture_angle = fields.Boolean(default=False, string='Show Picture Angle')
    show_picture = fields.Boolean(default=False, string='Show Picture')
    show_picture_top = fields.Boolean(default=False, string='Show Picture Top')
    show_picture_side1 = fields.Boolean(default=False, string='Show Picture Side1')
    show_picture_side2 = fields.Boolean(default=False, string='Show Picture side2')
    show_label_dimensions_width = fields.Boolean(default=False,
                                                 string='Show Label Dimensions Width')
    show_label_dimensions_height = fields.Boolean(default=False,
                                                  string='Show Label Dimensions Height')
    show_printed_can = fields.Boolean(default=False, string='Show Printed Can')
    show_no_impressions_front = fields.Boolean(default=False,
                                               string='Show Number of impressions_front')
    show_no_impressions_back = fields.Boolean(default=False,
                                              string='Show Number of impressions_back')
    show_print_artork_pdf = fields.Boolean(default=False, string='Show Print Artwork PDF')
    show_notes = fields.Boolean(default=False, string='Show Notes')
    show_language = fields.Boolean(default=False, string='Show language')
    show_status = fields.Boolean(default=False, string='Show status')
    show_no_rings = fields.Boolean(default=False, string='Show Number of rings')
    # show_ = fields.Boolean(default=False, string='Show ')
