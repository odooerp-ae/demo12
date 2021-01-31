# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError
import itertools


class ProductCategory(models.Model):
    _inherit = 'product.category'

    create_variants_always =fields.Boolean('Create Variants Always',default=False)



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def create_variant_ids(self):
        Product = self.env["product.product"]

        for tmpl_id in self.with_context(active_test=False):
            # Handle the variants for each template separately. This will be
            # less efficient when called on a lot of products with few variants
            # but it is better when there's a lot of variants on one template.
            variants_to_create = []
            variants_to_activate = self.env['product.product']
            variants_to_unlink = self.env['product.product']
            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them

            variant_alone = tmpl_id._get_valid_product_template_attribute_lines().filtered(
                    lambda line: line.attribute_id.create_variant == 'always' and len(line.value_ids) == 1).mapped('value_ids')
            for value_id in variant_alone:
                updated_products = tmpl_id.product_variant_ids.filtered(
                    lambda product: value_id.attribute_id not in product.mapped('attribute_value_ids.attribute_id'))
                updated_products.write({'attribute_value_ids': [(4, value_id.id)]})
            # Determine which product variants need to be created based on the attribute
            # configuration. If any attribute is set to generate variants dynamically, skip the
            # process.
            # Technical note: if there is no attribute, a variant is still created because
            # 'not any([])' and 'set([]) not in set([])' are True.
            if not tmpl_id.has_dynamic_attributes():
                # Iterator containing all possible `product.attribute.value` combination
                # The iterator is used to avoid MemoryError in case of a huge number of combination.
                all_variants = itertools.product(*(
                    line.value_ids.ids for line in
                tmpl_id._get_valid_product_template_attribute_lines()._without_no_variant_attributes()
                ))
                # Set containing existing `product.attribute.value` combination
                existing_variants = {
                    frozenset(variant.attribute_value_ids.ids)
                    for variant in tmpl_id.product_variant_ids
                }
                # For each possible variant, create if it doesn't exist yet.
                for value_ids in all_variants:
                    value_ids = frozenset(value_ids)
                    if value_ids not in existing_variants:
                        variants_to_create.append({
                            'product_tmpl_id': tmpl_id.id,
                            'attribute_value_ids': [(6, 0, list(value_ids))],
                        })
                        if len(variants_to_create) > 1000:
                            raise UserError(_(
                                'The number of variants to generate is too high. '
                                'You should either not generate variants for each combination or generate them on demand from the sales order. '
                                'To do so, open the form view of attributes and change the mode of *Create Variants*.'))

            elif tmpl_id.categ_id.create_variants_always and tmpl_id.has_dynamic_attributes():
                all_variants = itertools.product(*(
                    line.value_ids.ids for line in
                    tmpl_id._get_valid_product_template_attribute_lines()._without_no_variant_attributes()
                ))
                # Set containing existing `product.attribute.value` combination
                existing_variants = {
                    frozenset(variant.attribute_value_ids.ids)
                    for variant in tmpl_id.product_variant_ids
                }
                # For each possible variant, create if it doesn't exist yet.
                for value_ids in all_variants:
                    value_ids = frozenset(value_ids)
                    if value_ids not in existing_variants:
                        variants_to_create.append({
                            'product_tmpl_id': tmpl_id.id,
                            'attribute_value_ids': [(6, 0, list(value_ids))],
                        })

            # Check existing variants if any needs to be activated or unlinked.
            # - if the product is not active and has valid attributes and attribute values, it
            #   should be activated
            # - if the product does not have valid attributes or attribute values, it should be
            #   deleted
            valid_value_ids = tmpl_id._get_valid_product_attribute_values()._without_no_variant_attributes()
            valid_attribute_ids = tmpl_id._get_valid_product_attributes()._without_no_variant_attributes()
            for product_id in tmpl_id.product_variant_ids:
                if product_id._has_valid_attributes(valid_attribute_ids, valid_value_ids):
                    if not product_id.active:
                        variants_to_activate += product_id
                else:
                    variants_to_unlink += product_id

            if variants_to_activate:
                variants_to_activate.write({'active': True})

            # create new products
            if variants_to_create:
                Product.create(variants_to_create)

            # unlink or inactive product
            # try in batch first because it is much faster
            try:
                with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                    variants_to_unlink.unlink()
            except Exception:
                # fall back to one by one if batch is not possible
                for variant in variants_to_unlink:
                    try:
                        with self._cr.savepoint(), tools.mute_logger('odoo.sql_db'):
                            variant.unlink()
                    # We catch all kind of exception to be sure that the operation doesn't fail.
                    except Exception:
                        # Note: this can still fail if something is preventing from archiving.
                        # This is the case from existing stock reordering rules.
                        variant.write({'active': False})

        return True




