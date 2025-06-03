import PyInstaller.__main__
import os
import shutil

def build_exe():
    # Temizlik
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('youtube_video_indirici.spec'):
        os.remove('youtube_video_indirici.spec')

    # PyInstaller ile exe oluşturma
    PyInstaller.__main__.run([
        'app.py',
        '--name=YouTube_Video_Indirici',
        '--onefile',
        '--windowed',
        '--icon=icon.ico',
        '--add-data=requirements.txt;.',
        '--hidden-import=streamlit',
        '--hidden-import=yt_dlp',
        '--hidden-import=requests',
        '--hidden-import=cryptography',
    ])

    # Gerekli dosyaları kopyala
    shutil.copy('requirements.txt', 'dist/')
    shutil.copy('README.md', 'dist/')
    shutil.copy('LICENSE', 'dist/')

    print("Build tamamlandı! Exe dosyası 'dist' klasöründe.")

if __name__ == '__main__':
    build_exe() 