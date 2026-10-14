"""Command-line interface: python -m inventory <command>."""
import argparse
import sys

from .db import Inventory


def build_parser():
    p = argparse.ArgumentParser(prog="inventory", description="Manage a small inventory.")
    p.add_argument("--db", default="inventory.db", help="SQLite file (default: inventory.db)")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="add a new item")
    a.add_argument("name")
    a.add_argument("quantity", type=int)
    a.add_argument("price", type=float)

    l = sub.add_parser("list", help="list items")
    l.add_argument("--search", default="")

    s = sub.add_parser("stock", help="change stock level (+/- amount)")
    s.add_argument("name")
    s.add_argument("delta", type=int)

    r = sub.add_parser("remove", help="delete an item")
    r.add_argument("name")

    sub.add_parser("value", help="total inventory value")

    lo = sub.add_parser("low", help="items at or below a stock threshold")
    lo.add_argument("--threshold", type=int, default=5)
    return p


def main(argv=None, out=sys.stdout):
    args = build_parser().parse_args(argv)
    inv = Inventory(args.db)
    try:
        if args.command == "add":
            item = inv.add(args.name, args.quantity, args.price)
            print(f"Added {item.name} (x{item.quantity} @ ${item.price:.2f})", file=out)
        elif args.command in ("list", "low"):
            items = inv.list(args.search) if args.command == "list" else inv.low_stock(args.threshold)
            if not items:
                print("No items.", file=out)
            for i in items:
                print(f"{i.id:>3}  {i.name:<20} {i.quantity:>5}  ${i.price:>8.2f}", file=out)
        elif args.command == "stock":
            print(f"{args.name}: {inv.adjust(args.name, args.delta)} in stock", file=out)
        elif args.command == "remove":
            inv.remove(args.name)
            print(f"Removed {args.name}", file=out)
        elif args.command == "value":
            print(f"Total value: ${inv.total_value():,.2f}", file=out)
    except KeyError as e:
        print(f"error: no such item {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0
