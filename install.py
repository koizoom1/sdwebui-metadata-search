import launch

# 必要なライブラリ
requirements = ["pillow", "pandas"]

for package in requirements:
    if not launch.is_installed(package):
        launch.run_pip(f"install {package}", f"sd-webui-{package}")
