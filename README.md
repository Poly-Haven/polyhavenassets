# Poly Haven Assets Add-on

A Blender add-on to integrate our assets natively in the asset browser.

![Screenshot](/screenshot.jpg)

## Features

1. Downloads all assets from [Poly Haven](https://polyhaven.com/), and list them under their respective categories in the Asset Browser.
2. Lets you swap the resolution of an asset to higher/lower resolutions any time after import (most are at least 8K).
3. Set the texture mapping scale to the correct real-world size according to the surfaces you've applied it to.
4. One-click setup of texture displacement with adaptive subdivision.
5. Simple HDRI rotation, brightness, and color temperature sliders.

## Installation

This add-on is meant to be purchased on [Superhive](https://superhivemarket.com/products/poly-haven-asset-browser) or through [Patreon](https://www.patreon.com/posts/70974704) to support our work making new assets.

> ## **Help make this add-on free for everyone!**
>
>  While all [our assets](https://polyhaven.com/all) are 100% free to download, it costs us a lot to create them. By selling this add-on, we've been able to grow Poly Haven, creating over 1000 new assets and improving the quality of our work.
>
> **However, we don't want to sell this add-on forever, we want to focus on free content and open access.**
>
> [Support us on Patreon](https://www.patreon.com/join/polyhaven/checkout?rid=6545111) with just $5 per month to get this add-on and help unlock it for the entire community. Once we reach 5000 patrons, it will be released for free to everyone. Until then, it's available only through Patreon, or by purchasing it on Superhive.
>
> [Read more about liberating this add-on](https://blog.polyhaven.com/liberating-our-blender-add-on/).
>
> [![roadmapImg](https://polyhaven.com/api/roadmapImg?m=light)](https://polyhaven.com/vaults)

1. Download the ZIP file...
    * From your [Superhive account page](https://superhivemarket.com/account/orders) if you purchased it there ($69).
    * From [this post on Patreon](https://www.patreon.com/posts/blender-asset-70974704) if you support us there ($5/m).
2. In Blender 4.2 and newer, open `Edit > Preferences > Extensions`, click `Install from Disk...`, and select the ZIP file (do not unzip it first).
3. Enable the extension.

> Blender 4.2+ installs this package as an extension. Using the legacy add-on installer with a versioned ZIP can cause import errors such as `No module named 'polyhavenassets-1'`.

### Building from source

If you are packaging this repository yourself, build the distributable ZIP from the repository root with Blender's extension CLI:

```powershell
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --command extension build
```

This generates a Blender extension package using `blender_manifest.toml`, which is the expected format for Blender 4.2 and newer.

For more detailed instructions, please check our [video guide and documentation](https://docs.polyhaven.com/en/guides/blender-addon).

## Support

If you need help, please check out the [user guide and documentation](https://docs.polyhaven.com/en/guides/blender-addon) first, then contact us using the link at the bottom of that page.

## Usage

> [A more detailed user guide and video demo is available here](https://docs.polyhaven.com/en/guides/blender-addon).

1. After enabling the add-on, [add a new Asset Library](https://file.coffee/u/sPrJY2-9578l2WjmmOA3n.png) in your preferences called `Poly Haven`. This is where assets will be downloaded to.
2. Open the asset browser editor and select the Poly Haven library at the top left.
3. Click the ***Fetch Assets*** button in the header of the asset browser.
4. After the initial download (which currently is around 3.3GB), simply drag and drop the assets into your scene.
5. We release new assets almost daily, so you can click that *Fetch Assets* button any time to download new assets.

### Updating:

To check for a new version of the add-on, simply visit the add-on's Preferences in Blender and click the *Check now for update* button.

Alternatively, you can download the latest version and install it again from your [Superhive account page](https://superhivemarket.com/account/orders) or [this post on Patreon](https://www.patreon.com/posts/blender-asset-70974704).
