# Klee 1.0

Klee is an Android 17 platform distribution based directly on the Android Open
Source Project. The `Klee-1.0` branch starts from the exact
`android-17.0.0_r1` project histories and carries Klee changes as separate,
reviewable commits.

## Initialize the source tree

```bash
repo init -u https://github.com/KleeUI/android.git -b Klee-1.0
repo sync -c --force-sync --force-checkout --no-clone-bundle --no-tags -j4
```

## Select and build a device

Device repositories register their product using the device codename. Klee's
build environment accepts the compact `<device>_<variant>` lunch format:

```bash
source build/envsetup.sh
lunch cupid_userdebug
klee_build -j20
```

Supported variants are `user`, `userdebug`, and `eng`. The default Android 17
release configuration is `cp2a`. Klee does not impose a maximum parallel job
count; users select it with `klee_build -jXX` or `mka bacon -jXX`.

Hardware-specific device, kernel, and proprietary-vendor repositories are kept
separate from the platform source repositories.

Qualcomm platforms use optional manifests generated from pinned official
CodeLinaro releases. For example, initialize SM8450/Waipio support with:

```bash
repo init -u https://github.com/KleeUI/android.git \
    -b Klee-1.0 -m qcom/waipio.xml
```

See `qcom/README.md` for all supported Qualcomm platform manifests. Klee-owned
integration code is independently implemented; AOSP and Qualcomm dependencies
retain their real upstream history and attribution.

Binary prebuilt projects remain pinned to their exact AOSP 17 revisions on
`android.googlesource.com`. GitHub cannot store several of their original
histories without rewriting large files, so Klee deliberately keeps those
immutable dependencies on the authoritative AOSP remote.

The same rule applies to the small number of AOSP source projects whose pinned
history contains individual objects above GitHub's 100 MiB hard limit. Core
projects available from GitHub's official `aosp-mirror` network are forked
server-side instead, preserving their exact AOSP commit identities.
