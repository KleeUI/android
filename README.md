# Klee 1.0

Klee is an Android 17 platform distribution based directly on the Android Open
Source Project. The `Klee-1.0` branch starts from the exact
`android-17.0.0_r1` project histories and carries Klee changes as separate,
reviewable commits.

**中文使用与自行编译：** [Xiaomi 12 / Cupid 完整指南](https://github.com/KleeUI/android_device_xiaomi_cupid/blob/Klee-1.0/docs/BUILDING.zh-CN.md)
（Linux 环境、专有输入、整包构建、产物、设备检查和常见问题）。

## Initialize the source tree

For Xiaomi 12 (`cupid`, SM8450), select the Waipio manifest in a new Linux
working directory. A standalone clone of the device repository is not a full
Android checkout.

```bash
mkdir -p "$HOME/android/klee"
cd "$HOME/android/klee"
repo init -u https://github.com/KleeUI/android.git \
    -b Klee-1.0 -m qcom/waipio.xml
repo sync -c --no-clone-bundle --no-tags -j4
```

The default manifest alone does not include the Cupid device and complete
Waipio platform inputs. The selected manifest supplies the kernel and source
DT links; do not replace them with an unrelated kernel or stock DTB/DTBO.
Use `repo status` and save local changes before subsequent synchronizations.

## Prepare Cupid proprietary inputs

The public Waipio manifest does not populate the complete
`vendor/xiaomi/cupid` and `vendor/xiaomi/sm8450-common` trees. Provide compatible,
authorized inputs at those paths before building; the separately synced
`vendor/xiaomi/sm8450-qcril` project is not a replacement. Cupid's
`proprietary-files.txt` and `extract-files.py` cover a small device delta, not
the complete vendor inventory. See the
[device input workflow](https://github.com/KleeUI/android_device_xiaomi_cupid/blob/Klee-1.0/docs/BUILDING.zh-CN.md#4-准备完整专有输入和设备差量)
for the prerequisite and extraction steps.

After preparing the complete inputs and delta, run from the Android root:

```bash
python3 device/xiaomi/cupid/setup-makefiles.py
python3 device/xiaomi/cupid/setup-makefiles.py --check
```

Review the printed states. `--check` is read-only and can exit successfully
with `pending` entries; ready metadata should report `already-applied`.
Do not force a patch stack that reports drift.

## Select and build a device

Continue from the Android source root after installing the
[AOSP host dependencies](https://source.android.com/docs/setup/start/requirements)
and preparing the device inputs:

```bash
source build/envsetup.sh
lunch cupid-cp2a-userdebug
klee_build -j8
```

Supported variants are `user`, `userdebug`, and `eng`. The default Android 17
release configuration is `cp2a`. Klee does not impose a maximum parallel job
count; `8` is an example chosen by the user for the host's CPU and memory.
The compact `lunch cupid_userdebug` form is also supported when the Klee
environment is loaded. `klee_build` defaults to `droid` and builds the kernel
and modules inline; `mka bacon` is an alias for that full build, not a signing
or release-validation step.

To request packaging artifacts explicitly in the same environment:

```bash
klee_build -j8 target-files-package otapackage
```

The default output is `out/target/product/cupid/`; target-files archives are
under `obj/PACKAGING/target_files_intermediates/`. A generated image or OTA is
not by itself evidence of a validated installation path or complete hardware
support. The device guide covers artifact checks and the current development
signing and test boundaries.

Hardware-specific device, kernel, and proprietary-vendor repositories are kept
separate from the platform source repositories.

Qualcomm platforms use optional manifests generated from pinned official
CodeLinaro releases. See [qcom/README.md](qcom/README.md) for the other platform
manifests. Klee-owned
integration code is independently implemented; AOSP and Qualcomm dependencies
retain their real upstream history and attribution.

Before publishing a manifest change, validate that every declared source stays
inside the AOSP, CodeLinaro, and KleeUI boundary:

```bash
python3 tools/check_manifest_sources.py
```

Binary prebuilt projects remain pinned to their exact AOSP 17 revisions on
`android.googlesource.com`. GitHub cannot store several of their original
histories without rewriting large files, so Klee deliberately keeps those
immutable dependencies on the authoritative AOSP remote.

The same rule applies to the small number of AOSP source projects whose pinned
history contains individual objects above GitHub's 100 MiB hard limit. Core
projects available from GitHub's official `aosp-mirror` network are forked
server-side instead, preserving their exact AOSP commit identities.
