from pathlib import Path
import json
from datetime import date

from py7zr import SevenZipFile, Py7zIO, WriterFactory


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

ARCHIVE_FILE = Path(
    r"C:\Users\suman\Downloads\LGD_Panchayats.geojsonl.7z"
)

OUTPUT_DIR = BASE_DIR / "data" / "gis"
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = OUTPUT_DIR / "up_panchayats.geojsonl"

METADATA_FILE = OUTPUT_DIR / "up_panchayats_metadata.json"


# ============================================================
# TARGET
# ============================================================

TARGET_STATE = "uttar pradesh"


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value):
    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def is_up_feature(feature):
    """
    Identify Uttar Pradesh features.

    We first look for state-related property names.
    As a fallback, we check whether any property value
    exactly equals 'Uttar Pradesh'.
    """

    properties = feature.get("properties", {})

    if not isinstance(properties, dict):
        return False

    state_keys = []

    for key in properties:
        normalized_key = normalize(key)

        if (
            "state" in normalized_key
            or normalized_key in {
                "stname",
                "st name",
                "st_nm",
                "st nm",
                "st_name",
                "st name",
            }
        ):
            state_keys.append(key)

    # Preferred check
    for key in state_keys:

        if normalize(properties.get(key)) == TARGET_STATE:
            return True

    # Fallback check
    for value in properties.values():

        if normalize(value) == TARGET_STATE:
            return True

    return False


# ============================================================
# STREAMING WRITER
# ============================================================

class PanchayatFilterWriter(Py7zIO):

    def __init__(self, output_path):

        self.output_path = output_path

        self.output = open(
            output_path,
            "w",
            encoding="utf-8"
        )

        self.buffer = b""

        self.total_lines = 0
        self.up_features = 0
        self.invalid_lines = 0

        self.sample_properties = None
        self.sample_keys = None

    def write(self, data):

        if not data:
            return

        self.buffer += bytes(data)

        while b"\n" in self.buffer:

            line, self.buffer = self.buffer.split(
                b"\n",
                1
            )

            self.process_line(line)

    def process_line(self, line):

        line = line.strip()

        if not line:
            return

        self.total_lines += 1

        try:

            feature = json.loads(
                line.decode("utf-8")
            )

        except Exception:

            self.invalid_lines += 1
            return

        if self.sample_properties is None:

            properties = feature.get(
                "properties",
                {}
            )

            if isinstance(properties, dict):

                self.sample_properties = properties

                self.sample_keys = list(
                    properties.keys()
                )

        if is_up_feature(feature):

            self.output.write(
                line.decode("utf-8")
                + "\n"
            )

            self.up_features += 1

    def flush(self):

        if self.buffer.strip():

            self.process_line(
                self.buffer
            )

        self.buffer = b""

        self.output.flush()

    def read(self, size=None):
        return b""

    def seek(self, offset, whence=0):
        return 0

    def size(self):
        try:
            return self.output.tell()
        except Exception:
            return 0

    def close(self):

    if self.output.closed:
        return

    self.flush()
    self.output.close()

# ============================================================
# FACTORY
# ============================================================

class FilterFactory(WriterFactory):

    def __init__(self, output_path):

        self.output_path = output_path

        self.writer = None

    def create(self, filename):

        self.writer = PanchayatFilterWriter(
            self.output_path
        )

        return self.writer


# ============================================================
# MAIN
# ============================================================

print("=" * 60)
print("STREAMING UP PANCHAYAT EXTRACTION")
print("=" * 60)

print(
    f"Archive: {ARCHIVE_FILE}"
)

print(
    f"Output:  {OUTPUT_FILE}"
)

if not ARCHIVE_FILE.exists():

    raise FileNotFoundError(
        f"Archive not found:\n{ARCHIVE_FILE}"
    )


# Remove old output if present
if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()


factory = FilterFactory(
    OUTPUT_FILE
)


print()
print(
    "Reading the compressed archive..."
)

print(
    "The national 1.45 GB file will NOT "
    "be extracted to disk."
)

print()


try:

    with SevenZipFile(
        ARCHIVE_FILE,
        "r"
    ) as archive:

        archive.extract(
            targets=[
                "LGD_Panchayats.geojsonl"
            ],
            factory=factory
        )


except Exception as exc:

    if factory.writer is not None:

        factory.writer.close()

    raise exc


writer = factory.writer

if writer is None:

    raise RuntimeError(
        "No extraction writer was created."
    )




# ============================================================
# OUTPUT SIZE
# ============================================================

output_size_mb = (
    OUTPUT_FILE.stat().st_size
    / (1024 * 1024)
)


# ============================================================
# METADATA
# ============================================================

metadata = {

    "dataset": "LGD_Panchayats.geojsonl",

    "source_archive": (
        "LGD_Panchayats.geojsonl.7z"
    ),

    "source_archive_path": str(
        ARCHIVE_FILE
    ),

    "filter": {
        "state": "Uttar Pradesh"
    },

    "processing_date": str(
        date.today()
    ),

    "total_records_read": (
        writer.total_lines
    ),

    "uttar_pradesh_records": (
        writer.up_features
    ),

    "invalid_records": (
        writer.invalid_lines
    ),

    "output_file": str(
        OUTPUT_FILE
    ),

    "output_size_mb": round(
        output_size_mb,
        2
    ),

    "notes": (
        "Filtered locally from the public "
        "LGD Panchayat distribution. "
        "The national compressed archive "
        "was not committed to the project repository."
    ),

    "sample_property_keys": (
        writer.sample_keys
    ),
}


with open(
    METADATA_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("FILTER COMPLETE")
print("=" * 60)

print(
    f"Records read       : "
    f"{writer.total_lines:,}"
)

print(
    f"UP Panchayats      : "
    f"{writer.up_features:,}"
)

print(
    f"Invalid records    : "
    f"{writer.invalid_lines:,}"
)

print(
    f"Output size        : "
    f"{output_size_mb:.2f} MB"
)

print()
print(
    f"GeoJSONL: {OUTPUT_FILE}"
)

print(
    f"Metadata: {METADATA_FILE}"
)

print()
print("Sample property keys:")

if writer.sample_keys:

    for key in writer.sample_keys:
        print(f"  - {key}")

else:

    print("  No properties detected.")