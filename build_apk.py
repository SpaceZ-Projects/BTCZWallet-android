
import os
import subprocess
import sys
import shutil


def compare_versions(version1, version2):
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]

    while len(v1_parts) < len(v2_parts):
        v1_parts.append(0)
    while len(v2_parts) < len(v1_parts):
        v2_parts.append(0)

    if v1_parts > v2_parts:
        return 1
    elif v1_parts < v2_parts:
        return -1
    return 0


def get_python_versions():
    versions = set()
    try:
        output = subprocess.check_output(["py", "--list"], stderr=subprocess.DEVNULL)
        for line in output.decode().splitlines():
            line = line.strip()
            if line.startswith("-V:"):
                version_str = line.split(":")[1].strip().split()[0]
            elif line.startswith("-"):
                parts = line[1:].split("-")
                version_str = parts[0].strip()
            else:
                continue

            if compare_versions(version_str, "3.10") >= 0:
                versions.add(version_str)
    except subprocess.CalledProcessError:
        print("Could not find Python versions.")
    return sorted(versions)


def select_python_version():
    versions = get_python_versions()
    if not versions:
        print("[ERROR] No suitable Python versions found. Please install Python 3.10 or newer.")
        sys.exit(1)

    print("\nAvailable Python Versions:")
    for i, version in enumerate(versions, start=1):
        print(f"{i}. Python {version}")

    try:
        choice = int(input("Select the number corresponding to your preferred Python version: "))
        if 1 <= choice <= len(versions):
            return versions[choice - 1]
        else:
            raise ValueError
    except ValueError:
        print("[ERROR] Invalid selection.")
        sys.exit(1)


def create_virtualenv(env_name, python_version):
    print(f"[INFO] Creating virtual environment with Python {python_version}...")
    subprocess.check_call(["py", f"-{python_version}", "-m", "venv", env_name])


def upgrade_pip(env_path):
    print("[INFO] Upgrading pip...")
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'python.exe'), "-m", "pip", "install", "--upgrade", "pip"])


def install_briefcase(env_path):
    print("[INFO] Installing Briefcase...")
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'pip'), "install", "briefcase==0.3.24"])


def ensure_briefcase_installed(env_path):
    try:
        subprocess.check_call([os.path.join(env_path, 'Scripts', 'pip'), "show", "briefcase"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        install_briefcase(env_path)


def build_apk(env_path):
    print("[INFO] Building application...")
    build_dir = "build"
    if os.path.exists(build_dir):
        print("[INFO] Cleaning existing build...")
        shutil.rmtree(build_dir)
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'briefcase'), "build", "android"])


def move_apk_to_root():
    source_apk = os.path.join(
        "build", "BTCZWallet", "android", "gradle", "app",
        "build", "outputs", "apk", "debug", "app-debug.apk"
    )
    target_apk = os.path.join(os.getcwd(), "BTCZWallet.apk")
    if os.path.exists(source_apk):
        shutil.copy2(source_apk, target_apk)
        print(f"[INFO] APK moved and renamed to: {target_apk}")
        build_dir = "build"
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
    else:
        print("[ERROR] APK not found, build might have failed")


def main():
    
    env_dir = "env"
    if not os.path.exists(env_dir):
        python_version = select_python_version()
        create_virtualenv(env_dir, python_version)
        upgrade_pip(env_dir)

    ensure_briefcase_installed(env_dir)
    build_apk(env_dir)
    move_apk_to_root()

    input("\n[INFO] Process complete. Press Enter to exit...")


if __name__ == "__main__":
    main()
