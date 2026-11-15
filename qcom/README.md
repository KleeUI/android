# Qualcomm platform manifests

Klee keeps Qualcomm support as optional manifests because platform releases
use different revisions at the same source paths and therefore cannot all be
checked out into one working tree.

The files in this directory are generated directly from pinned CodeLinaro
release manifests. Klee-specific integration and build logic is developed
independently in Klee repositories; upstream Qualcomm code retains its original
history, license, and attribution.

Projects are shallow-synced at the exact release commit to keep large external
histories off the local Android work disk. This does not rewrite any source or
commit identity; full history remains available from the declared CodeLinaro
remote.

Initialize the required platform by selecting its manifest:

```bash
repo init -u https://github.com/KleeUI/android.git \
    -b Klee-1.0 -m qcom/waipio.xml
repo sync -c --no-clone-bundle --no-tags -j4
```

For Xiaomi 12 (`cupid`), follow the
[usage and build guide](https://github.com/KleeUI/android_device_xiaomi_cupid/blob/Klee-1.0/docs/BUILDING.zh-CN.md).
The public manifest supplies platform and kernel sources, but complete
`vendor/xiaomi/cupid` and `vendor/xiaomi/sm8450-common` proprietary inputs must
be prepared separately. A successful sync alone is not enough to build the
device. Save local modifications before updating an existing checkout.

Available manifests:

- `qssi16.xml`: QSSI 16 common system interface
- `waipio.xml`: SM8450
- `kailua.xml`: SM8550
- `lanai.xml`: SM8650
- `pakala.xml`: SM8750
- `lahaina.xml`: SM8350

Pinned upstream releases are recorded in the XML comments. Regenerate a file
with `tools/generate_qcom_manifest.py` after checking out the corresponding
official CodeLinaro manifest tag.
