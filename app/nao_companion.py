from nao.config import ASSET_DIR
from nao.ui import NaoApp


def main():
    atlas = ASSET_DIR / "uniform.png"
    if not atlas.exists():
        raise SystemExit(f"Missing sprite asset: {atlas}")
    NaoApp().run()


if __name__ == "__main__":
    main()
