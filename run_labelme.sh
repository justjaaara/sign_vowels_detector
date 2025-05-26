#!/bin/bash

# Set Qt environment variables
export QT_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms
export QT_QPA_PLATFORM=xcb
export QT_NO_PLUGIN_PATH=1
export QT_DEBUG_PLUGINS=1
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu/qt5:$LD_LIBRARY_PATH
export QT_LOGGING_RULES="qt.qpa.*=true"
export QT_XCB_GL_INTEGRATION=none

# Unset variables that might interfere
unset PYTHONPATH

# Activate the virtual environment
source /home/felipe/Desktop/Vocales/venv/bin/activate

# Run labelme with explicit Python call
python -c "import sys; print('Python:', sys.version); print('Paths:', sys.path); import cv2; print('OpenCV:', cv2.__version__, 'Path:', cv2.__file__)"
echo "Starting labelme..."
python -m labelme

# Deactivate the virtual environment when done
deactivate

