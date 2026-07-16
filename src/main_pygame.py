from __future__ import annotations
import argparse
from .ui.pygame_app import App

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--algo", choices=["independent","prioritized","cbs"], default="cbs")
    args = ap.parse_args()
    App(args.scenario, args.algo).loop()

if __name__ == "__main__":
    main()
