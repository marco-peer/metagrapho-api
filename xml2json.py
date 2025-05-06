import xml.etree.ElementTree as ET
import json

def parse_coords_str(coords_str):
    return {"points": coords_str.strip()}

def convert_xml2json(xml_string):
    ns = {
        'pc': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'
    }

    root = ET.fromstring(xml_string)
    page = root.find('pc:Page', ns)

    content = {
        "regions": []
    }

    for region in page.findall('.//pc:TextRegion', ns):
        region_data = {
            "id": region.get("id"),
            "coords": parse_coords_str(region.find('pc:Coords', ns).get('points')),
            "lines": []
        }

        for line in region.findall('pc:TextLine', ns):
            line_data = {
                "id": line.get("id"),
                "coords": parse_coords_str(line.find('pc:Coords', ns).get('points')),
                "baseline": parse_coords_str(line.find('pc:Baseline', ns).get('points'))
            }
            region_data["lines"].append(line_data)

        content["regions"].append(region_data)

    return content

