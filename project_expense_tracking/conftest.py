import os
import sys
project_root= os.path.join(os.path.dirname(__file__), '...')
print("Project Root:",project_root)
sys.path.insert(0,project_root)
print(sys.path)