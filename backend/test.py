import sys
print("Python path:", sys.path)
try:
    import main
    print("Successfully imported main module")
except ImportError as e:
    print("Error importing main module:", e) 