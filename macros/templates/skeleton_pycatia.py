"""skeleton_pycatia.py

Python equivalent of Skeleton.CATScript using pycatia (https://pycatia.readthedocs.io).
Requires: Windows, CATIA V5 running, `pip install pycatia`.

Run from any terminal on the CATIA machine:  python skeleton_pycatia.py
"""
from pycatia import catia


def main() -> None:
    caa = catia()
    doc = caa.active_document
    if doc is None:
        print("Open a document first.")
        return

    # pycatia exposes typed wrappers; the underlying COM object is .com_object
    kind = doc.com_object.__class__.__name__
    if not doc.is_product:
        print(f"This script expects a product. Active document is {doc.name} ({kind}).")
        return

    product = doc.product
    print(f"Active product: {product.part_number} with {product.products.count} direct children.")

    for child in product.products:
        print(f"  {child.part_number}  ({child.name})")


if __name__ == "__main__":
    main()
