Pyxml
------
Pure python3 alternative to stdlib xml.etree with HTML support

### Install

```
pip install pyxml3
```

### Advantages

The primary advantage of this library over stdlib or lxml is the completeness
of it's XPATH implementation. Additional functions and features are supported
allowing for more complex queries and simplifying parsing efforts.

### Examples

###### Standard Usage:

```python
import pyxml

etree = pyxml.fromstring(b'<p>Hello World!</p>')
for element in etree.iter():
  print(element)

with open('example.xml', 'rb') as f:
  etree = pyxml.fromstring(f)
  print(etree)
```

###### Monkey Patch:

```python
import pyxml
pyxml.compat.monkey_patch()

from xml.etree import ElementTree as ET

etree = ET.fromstring('<div><p class="hello world">Hello World!</p></div>')
for element in etree.iter():
  print(element)

print(etree.find('//p[starts-with(lower-case(text()), "hello")]'))
```

###### HTML:

```python
import pyxml.html

etree = pyxml.html.fromstring('<div><p>Hello World!</p><br></div>')
for element in etree.iter():
  print(element)

print(etree.find('//p[notempty(text())]'))
```

