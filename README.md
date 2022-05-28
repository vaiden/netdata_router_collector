# Nedata Router Collector
A collection of Netdata collectors for different routers.
Currently supported:
- Sagemcom F@ST (full list on [python-sagemcom-api](https://github.com/iMicknl/python-sagemcom-api](https://github.com/iMicknl/python-sagemcom-api#supported-devices))).
- Xiaomi MiWiFi

## We want YOU
Want to add a new type of router or a new chart to an existing one? Please PR.

## Roadmap
This started as an effort to track a Sagecom F@ST using Netdata. Now more routers are added.
Eventually the whole project will be bundled as a single collector with multiple plugins.
### When?
Depends. I'm still quite new to the Netdata ecosystem (so far: great people, appaling dev experience).

## Installing
```bash
$ sudo mv xiaomi.chart.py /usr/lib/netdata/python.d/
$ sudo mv xiaomi.conf /usr/lib/netdata/conf.d/python.d/
$ cd /etc/netdata
$ sudo ./edit-config python.d/xiaomi.conf
```
Add this to your `netdata.conf`:
```yaml
[plugins]
  python.d = yes

[plugin:python.d]
	command options = -ppython3
```
Then:
```bash
$ sudo ./edit-config python.d.conf
```
And enable your collector:
```
xiaomi: yes
```
Now let's test the collector:
```bash
$ /usr/lib/netdata/plugins.d/python.d.plugin debug trace xiaomi
```
No errors? Great. Let's restart Netdata:
```bash
$ sudo systemctl restart netdata
```
----
Still a WIP due to https://github.com/netdata/netdata/discussions/13017.
