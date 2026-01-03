#!/usr/bin/env python
"""Script wrapper pour exécuter le script d'autovote."""
import sys
from pathlib import Path

# Ajouter le répertoire src au path pour permettre les imports
root_path = Path(__file__).parent
src_path = root_path / "src"
sys.path.insert(0, str(src_path))

# Exécuter le module
if __name__ == "__main__":
    try:
        from excalia_autovote.main import main
        sys.exit(main())
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("\n💡 Assurez-vous d'avoir installé le package avec:")
        print("   pip install -e .")
        print("\nOu utilisez la commande:")
        print("   python -m excalia_autovote.main")
        sys.exit(1)

