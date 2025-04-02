#!/bin/bash

echo "Installing IP Grabber tool..."

if ! command -v python3 &> /dev/null; then
    echo "Python not found. Installing Python..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm python python-pip
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y python3 python3-pip
    else
        echo "ERROR: Could not detect package manager!"
        echo "Please install Python 3 and pip manually"
        exit 1
    fi
else
    echo "Python is already installed."
fi

echo "Installing required libraries..."
pip3 install --user PyQt5 PyQtWebEngine requests

if command -v apt-get &> /dev/null; then
    sudo apt-get install -y python3-pyqt5.qtwebengine
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3-qt5-webengine
fi

echo "Creating run script..."
cat > run.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
cd "$SCRIPT_DIR" || exit
python3 src/main.py
EOF
chmod +x run.sh

echo -e "\nInstallation complete!"
echo -e "To run the IP Grabber tool:\n"
echo -e "  ./run.sh\n"
echo -e "Note: If you get library errors, you may need to install additional packages:"
echo -e "Debian/Ubuntu: sudo apt-get install python3-pyqt5.qtwebengine"
echo -e "Fedora/RHEL: sudo dnf install python3-qt5-webengine"