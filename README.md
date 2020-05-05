# animedl

A CLI tool to download anime from different anime streaming services. Keep in mind that some of these services may require Premium authorization. This is just a passion project and meant only for educational purposes. Please consider supporting the animation studios by paying for these services regardless of if there exists a bypass.

## Sites supported:

### Common
These features may be implemented in the future for all the sites below. There is no ETA on any of these features
- [ ] RSS feed
- [ ] Notifications for events (Telegram / Discord)
- [ ] API access

### Crunchyroll (mode: `--cr`)
**Features:** The following features are implemented. This readme will also document future features that I plan to develop
- [x] Single Episode Download
- [x] Automated `.ass` subtitle download and muxing (enUS)
- [x] Proxy support with smart proxy switching (for out of region content)
- [x] Whole series download
- [ ] Fonts support for modifying `.ass` subtitles before muxing
- [x] Multithreaded downloads for complete series
- [ ] Multi sub support
- [x] Search functionality

### Funimation
**Features:** The following features are implemented. This readme will also document future features that I plan to develop
- [x] Single Episode Download
- [x] Automated `.srt` subtitle download and muxing (enUS)
- [x] Proxy support (for out of region content)
- [ ] Smart proxy switching
- [ ] Whole series download
- [x] Multithreaded downloads for complete series
- [ ] Multi sub support
- [ ] Search functionality

### KissAnime
- Coming soon

## Proxy Setup:
As of now only HTTP and HTTPS based proxies are supported. SOCK5 proxy support will be added soon. To setup proxy access, please refer to the `proxy.json.sample` file to check the format. I have only tested this with nordvpn proxies, but it should work for any reliable proxy just fine.

## Usage:
Usage of this tool is fairly simple.

This tool has 3 required arguments: `mode`, `url`, `res`
```
$ python animedl.py --<mode> <url> <res>
```
Additionally, a path argument can be specified after these three using `--path <path>`. This will save the file at that specific path instead of the current working directory

## Contributing:
If you wish to contribute to the project, feel free to make PR, they are always welcome! Just make sure to follow the license terms when reusing any work in other projects, and support the animation studios if you can :)

## Credits:
- [anime-dl](https://github.com/Xonshiz/anime-dl): Some of the logic for the code was referenced from this repository. It is licensed under an MIT license which can be found [here](https://github.com/Xonshiz/anime-dl/blob/master/LICENSE)