
import re
from collections import Counter


# =============================================================================
# Utilidades de preprocesamiento
# =============================================================================

def normalize_text(text: str) -> str:
    """
    Limpia y estandariza el texto para poder analizarlo:
      - convierte a minúsculas
      - reemplaza signos/puntuación por espacios
      - elimina guiones bajos
      - reduce múltiples espacios a uno
      - conserva letras Unicode (tildes/ñ) y números
    """
    if not isinstance(text, str):
        raise TypeError("Entrada inválida: se requiere una cadena de texto (str).")

    text = text.lower()

    # Reemplazar todo lo que no sea letra/número/espacio por espacio
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)

    # Quitar '_' porque \w lo considera válido
    text = text.replace("_", " ")

    # Compactar espacios y recortar
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """
    Convierte el texto normalizado en tokens (palabras/números).
    Si está vacío, devuelve una lista vacía.
    """
    if not text:
        return []
    return text.split()


# =============================================================================
# Núcleo de análisis
# =============================================================================

class TextAnalyzer:
    """
    Orquesta el análisis de texto: normalización -> tokenización -> conteo.

    Atributos:
        original_text    : texto tal cual
        normalized_text  : texto ya normalizado
        tokens           : lista de tokens
        counts           : frecuencia por token (Counter)
        unique_tokens    : conjunto de tokens únicos
    """

    def __init__(self, text: str) -> None:
        if not text or not text.strip():
            raise ValueError("No se puede analizar un texto vacío.")
        self.original_text: str = text
        self.normalized_text: str = ""
        self.tokens: list[str] = []
        self.counts: Counter = Counter()
        self.unique_tokens: set[str] = set()

    def analyze(self) -> None:
        """Ejecuta todo el flujo de análisis."""
        self.normalized_text = normalize_text(self.original_text)
        self.tokens = tokenize(self.normalized_text)

        if not self.tokens:
            raise ValueError("No se encontraron tokens válidos después de normalizar.")

        self.counts = Counter(self.tokens)
        self.unique_tokens = set(self.tokens)

    def report(self) -> str:
        """
        Devuelve (y muestra) un reporte con las métricas principales.
        """
        if not self.tokens:
            raise RuntimeError("Debe ejecutar analyze() antes de generar el reporte.")

        total = len(self.tokens)
        unique = len(self.unique_tokens)
        top10 = self.counts.most_common(10)
        avg_len = sum(len(t) for t in self.tokens) / total

        lengths = {len(t) for t in self.tokens}
        max_len = max(lengths)
        min_len = min(lengths)
        longest = sorted({t for t in self.unique_tokens if len(t) == max_len})
        shortest = sorted({t for t in self.unique_tokens if len(t) == min_len})

        lines = [
            "╔" + "═" * 62 + "╗",
            "║" + " " * 18 + "REPORTE DEL ANÁLISIS DE TEXTO" + " " * 16 + "║",
            "╠" + "═" * 62 + "╣",
            f"║  Tokens totales          : {total:<37}║",
            f"║  Tokens únicos           : {unique:<37}║",
            f"║  Longitud promedio       : {avg_len:<37.2f}║",
            f"║  Más largo(s)            : {(', '.join(longest)):<37}║",
            f"║  Más corto(s)            : {(', '.join(shortest)):<37}║",
            "╠" + "═" * 62 + "╣",
            "║  Top 10 tokens más frecuentes:" + " " * 33 + "║",
            "╟" + "─" * 62 + "╢",
        ]

        for i, (token, count) in enumerate(top10, start=1):
            pct = count / total * 100
            row = f"{i:>2}. {token:<18} {count:>5} ({pct:>5.1f}%)"
            lines.append(f"║  {row:<58}║")

        lines.append("╚" + "═" * 62 + "╝")

        report_str = "\n".join(lines)
        print(report_str)
        return report_str

    def query(self, word: str) -> str:
        """
        Consulta cuántas veces aparece una palabra.
        Clasificación:
          - 1 vez  -> "rara"
          - >= 5   -> "común"
          - resto  -> "media"
        """
        if not self.tokens:
            raise RuntimeError("Debe ejecutar analyze() antes de consultar.")

        word_norm = normalize_text(word)
        if not word_norm:
            return "La palabra ingresada no tiene caracteres válidos."

        freq = self.counts.get(word_norm, 0)
        total = len(self.tokens)

        if freq == 0:
            return f"'{word_norm}' no se encontró en el texto."

        pct = freq / total * 100
        if freq == 1:
            label = "rara (1 vez)"
        elif freq >= 5:
            label = "común (≥ 5)"
        else:
            label = "media"

        return f"'{word_norm}' -> {freq} vez/veces ({pct:.2f}%), categoría: {label}"


# =============================================================================
# Entrada de datos
# =============================================================================

def load_from_file(path: str) -> str:
    """
    Lee un archivo .txt (UTF-8) y devuelve el contenido.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"No existe el archivo: '{path}'")
    except IsADirectoryError:
        raise IsADirectoryError(f"La ruta apunta a un directorio: '{path}'")
    except PermissionError:
        raise PermissionError(f"No tiene permisos para leer: '{path}'")
    except OSError as e:
        raise OSError(f"Error de sistema al leer el archivo: {e}")

    if not content.strip():
        raise ValueError("El archivo está vacío.")
    return content


def load_from_console() -> str:
    """
    Captura texto por consola hasta que el usuario escriba 'END'.
    """
    print("\n┌──────────────────────────────────────────────────────┐")
    print("│ Pegue o escriba su texto. Para finalizar escriba END │")
    print("└──────────────────────────────────────────────────────┘")

    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break

        if line.strip().upper() == "END":
            break
        lines.append(line)

    text = "\n".join(lines)
    if not text.strip():
        raise ValueError("No se ingresó ningún texto.")
    return text


# =============================================================================
# UI de consola (menús)
# =============================================================================

def _header() -> None:
    print("\n" + "╔" + "═" * 62 + "╗")
    print("║" + " " * 15 + "ANALIZADOR DE TEXTO — CONSOLA" + " " * 16 + "║")
    print("╚" + "═" * 62 + "╝")


def _menu_main() -> str:
    print("\n┌──────────────── MENÚ PRINCIPAL ────────────────┐")
    print("│  1) Cargar texto desde archivo (.txt)          │")
    print("│  2) Ingresar texto manualmente (pegar/teclear) │")
    print("│  3) Salir                                      │")
    print("└───────────────────────────────────────────────┘")
    return input("Seleccione una opción (1/2/3): ").strip()


def _menu_actions() -> str:
    print("\n┌───────────────── ACCIONES ────────────────────┐")
    print("│  1) Ver reporte completo                       │")
    print("│  2) Consultar frecuencia de una palabra        │")
    print("│  3) Analizar otro texto                        │")
    print("│  4) Salir                                      │")
    print("└───────────────────────────────────────────────┘")
    return input("Seleccione una opción (1/2/3/4): ").strip()


# =============================================================================
# Programa principal
# =============================================================================

def main() -> None:
    _header()

    while True:
        option = _menu_main()

        if option == "3":
            print("\n👋 Programa finalizado. ¡Éxitos!")
            return

        try:
            if option == "1":
                path = input("\nRuta del archivo (.txt): ").strip()
                text = load_from_file(path)
                print(f"\n✅ Archivo cargado correctamente ({len(text)} caracteres).")
            elif option == "2":
                text = load_from_console()
                print(f"\n✅ Texto recibido correctamente ({len(text)} caracteres).")
            else:
                print("\n⚠️  Opción no válida. Intente otra vez.")
                continue
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError, ValueError) as e:
            print(f"\n❌ Error al obtener el texto: {e}")
            continue

        # Analizar
        try:
            analyzer = TextAnalyzer(text)
            analyzer.analyze()
            print("\n✅ Análisis completado.")
        except (TypeError, ValueError, RuntimeError) as e:
            print(f"\n❌ Error durante el análisis: {e}")
            continue

        # Acciones post-análisis
        while True:
            action = _menu_actions()

            if action == "1":
                print()
                analyzer.report()

            elif action == "2":
                word = input("\nIngrese la palabra a consultar (o 'back' para regresar): ").strip()
                if word.lower() == "back":
                    continue
                if not word:
                    print("⚠️  No puede ir vacío.")
                    continue
                print(analyzer.query(word))

            elif action == "3":
                print("\n↩️  Volviendo al menú principal para analizar otro texto...")
                break

            elif action == "4":
                print("\n👋 Programa finalizado. ¡Éxitos!")
                return

            else:
                print("\n⚠️  Opción no válida. Intente otra vez.")


if __name__ == "__main__":
    main()
