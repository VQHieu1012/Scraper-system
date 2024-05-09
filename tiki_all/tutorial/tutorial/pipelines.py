# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class TutorialPipeline:
    def process_item(self, item, spider):
        

        adapter = ItemAdapter(item)
        

        # Strip all whitespace 
        field_names = adapter.field_names()
        
        for field_name in field_names:
            try:
                value = adapter.get(field_name)
                adapter[field_name] = value.strip()
            except:
                pass
        
        # Lowercase
        lower_keys = ['URL']
        for lower_key in lower_keys:
            value = adapter.get(lower_key)
            adapter[lower_key] = value.lower()

        # Convert to float
        float_keys = ['Rating', 'Sold_nbr', 'Price', 'Day_ago_created']
        for float_key in float_keys:
            value = adapter.get(float_key)
            adapter[float_key] = float(value)

        return item


