import pandas as pd
import re


class Cleaner():

    def __init__(self) -> None:
        self.keys = ['Link', 'Brand', 'Name', 'Price',
                      'Available Sizes', 'Available Colors']
        self._mc_keys = set()
        self._sf_keys = set()
        self._d_keys = set()
        self.sep = ';'

    # Helpers
    def _max_price_to_float(self, prices):
        if not prices:
            return None
        def _to_float(p):
            p = p.replace(',', '.').replace('€', '').strip()
            return float(p)
        return max([_to_float(p) for p in prices])

    def _sold_to_int(self, sold_label):
        if not sold_label:
            return 0
        try:
            return int(sold_label[-1].replace('-', '')
                                    .replace('%', ''))
        except:
            return 0
        
    def _clean_price(self, price_label: str):
        price = self._max_price_to_float(re.findall(r'\b\d{1,2},\d{2}\xa0€', price_label))
        sold = self._sold_to_int(re.findall(r'-\d{1,2}%', price_label))
        return (price, sold)

    def _clean_sizes(self, sizes: dict):
        available_sizes = [s for s in sizes if sizes.get(s, {}).get('count') != 'Notify Me']
        return self.sep.join(available_sizes)
    
    def _clean_colors(self, colors: dict):
        return self.sep.join(colors)

    def _clean_material_care(self, mc: dict):
        self._mc_keys.update(mc.keys())
        return mc

    def _clean_size_fit(self, sf: dict):
        self._sf_keys.update(sf.keys())
        return sf

    def _clean_details(self, d: dict):
        self._d_keys.update(d.keys())
        return d

    def clean(self, article_details: dict):

        _price_label = article_details.get('price_label')
        _colors = article_details.get('available_colors')
        _sizes = article_details.get('available_sizes')
        _material_care = article_details.get('other_details', {}).get('Material & care')
        _size_fit = article_details.get('other_details', {}).get('Size & fit')
        _details = article_details.get('other_details', {}).get('Details')
        
        price, sold = self._clean_price(_price_label)
        sizes = self._clean_sizes(_sizes)
        colors = self._clean_colors(_colors)
        material_care = self._clean_material_care(_material_care)
        size_fit = self._clean_size_fit(_size_fit)
        details = self._clean_details(_details)

        return {'Link': article_details.get('link'),
                'Brand': article_details.get('brand_name'),
                'Name': article_details.get('article_name'),
                'Price': price,
                'sold': sold,
                'Available Sizes': sizes,
                'Available Colors': colors,
                **material_care,
                **size_fit,
                **details}