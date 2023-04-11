import pandas as pd


class Cleaner():

    def __init__(self) -> None:
        self.keys = ['Link', 'Brand', 'Name', 'Price',
                      'Available Sizes', 'Available Colors']
        self._mc_keys = set()
        self._sf_keys = set()
        self._d_keys = set()
        self.sep = '\n'

    def _clean_price(self, price_label: str):
        return price_label.split('|')[0].strip()

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
        
        price = self._clean_price(_price_label)
        sizes = self._clean_sizes(_sizes)
        colors = self._clean_colors(_colors)
        material_care = self._clean_material_care(_material_care)
        size_fit = self._clean_size_fit(_size_fit)
        details = self._clean_details(_details)

        return {'Link': article_details.get('link'),
                'Brand': article_details.get('brand_name'),
                'Name': article_details.get('article_name'),
                'Price': price,
                'Available Sizes': sizes,
                'Available Colors': colors,
                **material_care,
                **size_fit,
                **details}