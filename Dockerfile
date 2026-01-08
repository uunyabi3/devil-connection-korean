FROM python:3.11-slim

WORKDIR /app

RUN apt update && apt install -y \
    gcc g++ make binutils file wget fuse \
    libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
    libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-cursor0 \
    libxkbcommon-x11-0 libxkbcommon0 libdbus-1-3 libgl1 libglib2.0-0 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pyinstaller

RUN wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O /usr/local/bin/appimagetool && \
    chmod +x /usr/local/bin/appimagetool && \
    cd /usr/local/bin && \
    ./appimagetool --appimage-extract && \
    mv squashfs-root appimagetool-dir && \
    ln -sf /usr/local/bin/appimagetool-dir/AppRun /usr/local/bin/appimagetool-extracted

COPY . .

RUN pyinstaller linux.spec && \
    mkdir -p AppDir/usr/bin && \
    mkdir -p AppDir/usr/share/applications && \
    mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps && \
    cp dist/DevilConnection-Patcher-Linux AppDir/usr/bin/DevilConnection-Patcher-Linux-x86_64 && \
    echo "[Desktop Entry]\nType=Application\nName=DevilConnection Patcher\nExec=DevilConnection-Patcher-Linux-x86_64\nIcon=devilconnection-patcher\nCategories=Utility;" > AppDir/usr/share/applications/devilconnection-patcher.desktop && \
    touch AppDir/usr/share/icons/hicolor/256x256/apps/devilconnection-patcher.png && \
    cd AppDir && \
    ln -sf usr/bin/DevilConnection-Patcher-Linux-x86_64 AppRun && \
    ln -sf usr/share/applications/devilconnection-patcher.desktop devilconnection-patcher.desktop && \
    ln -sf usr/share/icons/hicolor/256x256/apps/devilconnection-patcher.png devilconnection-patcher.png && \
    cd .. && \
    ARCH=x86_64 /usr/local/bin/appimagetool-extracted AppDir dist/DevilConnection-Patcher-Linux-x86_64.AppImage

CMD ["sh", "-c", "cp -r dist/* /output/"]