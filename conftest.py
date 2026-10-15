import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

backend_dir = os.path.join(project_root, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

fronted_dir = os.path.join(project_root, 'fronted')
if fronted_dir not in sys.path:
    sys.path.insert(0, fronted_dir)