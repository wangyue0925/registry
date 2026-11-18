# TRAE preview registry releases

This fork publishes a TRAE-only test registry for Zed. Its distribution version is
`0.216.0-preview.3`; the packaged binaries remain `0.216.0-alpha.3`.
The binary archives are downloaded directly from the TRAE CDN. GitHub Release
assets contain only the registry index, icon, original manifest, and checksums.

The source manifest is `traecli/preview-manifest.json`. Its original CDN URL is:

https://lf-cdn.trae.com.cn/obj/trae-com-cn/trae-cli/v2/acp/releases/0.216.0-preview.3/manifest.json

Its SHA-256 is `49bc9248072fe9d8c237ca6070be84769871ec8d9b2cc83852fc474a3569a7fa`.

## Build and release

Requires Python 3 and the GitHub CLI authenticated with write access to this fork.

```sh
python3 script/build-trae-preview.py
cd dist/trae-preview
shasum -a 256 -c SHA256SUMS
cd ../..
git push origin trae-preview-release
gh release create traecli-0.216.0-preview.3 \
  --repo wangyue0925/registry \
  --target "$(git rev-parse HEAD)" \
  --prerelease \
  --title 'TRAE CLI preview registry 0.216.0-preview.3' \
  --notes 'TRAE-only test index. Distribution 0.216.0-preview.3 packages binaries 0.216.0-alpha.3. Archives remain on the TRAE CDN.' \
  dist/trae-preview/registry.json \
  dist/trae-preview/traecli.svg \
  dist/trae-preview/manifest.json \
  dist/trae-preview/SHA256SUMS
```

Configure the test Zed build's `REGISTRY_URL` as:

```text
https://github.com/wangyue0925/registry/releases/download/traecli-0.216.0-preview.3/registry.json
```

No localhost HTTP server is needed. Rebuild Zed after changing this constant.
For another preview version, update the checked-in manifest, build and commit the
changes, publish a new tag, and update Zed's pinned release URL.

This test builder does not change the upstream schemas or stable agent metadata.
It directly emits the flattened preview index accepted by Zed. It does not run
the upstream stable-channel validation/authentication pipeline and does not
establish eligibility for an upstream Registry PR.
