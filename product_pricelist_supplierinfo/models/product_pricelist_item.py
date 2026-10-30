# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[("supplierinfo", "Prices based on supplier info")],
        ondelete={"supplierinfo": "set default"},
    )
    no_supplierinfo_min_quantity = fields.Boolean(
        string="Ignore Supplier Info Min. Quantity",
    )
    filter_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier filter",
        help="Only match prices from the selected supplier",
    )
    no_supplierinfo_discount = fields.Boolean(
        string="Ignore Supplier Info Discount",
        help=(
            "If checked, the discount set on the supplier info "
            "will be ignored in price calculation."
        ),
    )
    ignore_supplierinfo_margin = fields.Boolean(
        help="Based on supplierinfo price without sale margin applied"
    )

    def _compute_base_price(self, product, quantity, uom, *, currency=None, **kwargs):
        if self.base != "supplierinfo":
            return super()._compute_base_price(
                product, quantity, uom, currency=currency, **kwargs
            )
        # Price of the matching seller in the product's UoM and the rule's
        # currency; the rule's discount, rounding, surcharge and margins are
        # then applied by the standard computation. Sellers' minimum
        # quantities are in the product's UoM.
        if uom and uom != product.uom_id:
            quantity = uom._compute_quantity(quantity, product.uom_id)
        price = product.sudo()._get_supplierinfo_pricelist_price(
            self,
            date=kwargs.get("date") or self.env.context.get("date"),
            quantity=quantity,
        )
        price = product.uom_id._compute_price(price, uom or product.uom_id)
        return self._convert_price(
            price, self.currency_id, currency=currency, **kwargs
        )
