import barcode
from barcode.writer import SVGWriter


def generate_barcode_svg(uuid_obj):
    """Generate an SVG barcode from a UUID."""
    uuid_string = str(uuid_obj)  # Convert UUID to string
    barcode_class = barcode.get_barcode_class("code128")
    barcode_object = barcode_class(uuid_string, writer=SVGWriter())

    return barcode_object.render(
        writer_options={"module_width": 0.3, "module_height": 15}
    )
