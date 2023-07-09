from typing import IO

import statistics

import fitz
from PIL import Image, ImageOps


def _get_thumb_from_page(page: fitz.fitz.Page):
    pix = page.get_pixmap()
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

    return ImageOps.fit(img, (100, 150))


def get_thumbnail(
    pdf: str | None = None, stream: IO[bytes] | None = None
) -> tuple[int, Image.Image]:
    s = stream.read() if stream else None
    doc = fitz.open(filename=pdf, stream=s, filetype="pdf")

    # Iterate on the first 10 pages to find an interesting one to thumbnail
    for i in range(min(doc.page_count, 10)):
        page = doc[i]
        img = _get_thumb_from_page(page)

        # We convert the image to grayscale
        grayscale = img.convert("L")

        # Then cut the image horizontally the image in 3 slices
        top = grayscale.crop((0, 0, 100, 50))
        middle = grayscale.crop((0, 50, 100, 100))
        bottom = grayscale.crop((0, 100, 100, 150))

        # For each slice, we look at the std dev of all pixels (0 being black, 255 being white)
        devs = [
            statistics.stdev(top.getdata()),
            statistics.stdev(middle.getdata()),
            statistics.stdev(bottom.getdata()),
        ]

        # If at least 2 slices of the 3 contain something, we keep this page
        # (we check that the stddev is > 5, meaning there is some change in the pixel values
        # eg, a full white or full black slice has a stddev of 0, a slice with only a page number will
        # have a stddev of maybe 2 where a slice full of text might be around 20)
        if sum([x > 5 for x in devs]) >= 2:
            break
    else:
        # If we did not find an interesting page, keep the first one
        i = 0
        img = _get_thumb_from_page(doc[i])

    return i, img
