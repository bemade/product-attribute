# Copyright 2020 Akretion - Mourad EL HADJ MIMOUNE
# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    sale_margin = fields.Float(
        default=0,
        digits=(16, 2),
        string="Sale Margin (%)",
        help="Margin to apply on price to obtain sale price",
    )

    def _get_supplierinfo_pricelist_price(
        self, no_supplierinfo_discount=False, ignore_margin=False
    ):
        self.ensure_one()
        if no_supplierinfo_discount:
            # price_discounted is already in the product's UoM, price is not
            product_uom = (self.product_id or self.product_tmpl_id).uom_id
            sale_price = self.uom_id._compute_price(self.price, product_uom)
        else:
            sale_price = self.price_discounted
        if self.sale_margin and not ignore_margin:
            sale_price = (sale_price + (sale_price * (self.sale_margin / 100))) or 0.0
        return sale_price
