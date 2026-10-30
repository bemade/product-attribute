# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# Copyright 2019-2025 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_supplierinfo_pricelist_price(
        self,
        rule,
        date=None,
        quantity=None,
        product_id=None,
    ):
        """Price of the matching supplier info, in the product's UoM and the
        rule's currency (sale margin included unless ignored). The rule's own
        discount, rounding, surcharge and margins are not applied here."""
        self.ensure_one()
        price = 0.0
        product = self.product_variant_id
        if product_id:
            product = product.browse(product_id)
        if rule.no_supplierinfo_min_quantity:
            # No matter which minimum qty, we'll get every seller. We set a
            # number absurdidly high
            quantity = 1e9
        # The product_variant_id returns empty recordset if template is not
        # active, so we must ensure variant exists or _select_seller fails.
        if product:
            if isinstance(date, datetime):
                date = date.date()
            seller = product.with_context(
                override_min_qty=rule.no_supplierinfo_min_quantity
            )._select_seller(
                # For a public user this record could be not accessible, but we
                # need to get the price anyway
                partner_id=self.env.context.get(
                    "force_filter_supplier_id", rule.sudo().filter_supplier_id
                ),
                quantity=quantity,
                date=date,
            )
            if seller:
                price = seller._get_supplierinfo_pricelist_price(
                    rule.no_supplierinfo_discount,
                    ignore_margin=rule.ignore_supplierinfo_margin,
                )
        if price and rule.currency_id != seller.currency_id:
            # Express the price in the pricelist's currency
            convert_date = date or self.env.context.get("date", fields.Date.today())
            price = seller.currency_id._convert(
                price, rule.currency_id, seller.company_id, convert_date
            )
        return price
