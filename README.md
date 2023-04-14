Pyxml
------
Pure python3 alternative to stdlib xml.etree with HTML support

### Install

```
pip install pyxml3
```

### Advantages

1. The default parser ignores XML Declaration Entities avoiding 
   most if not all XML related vulnerabilities such as 
   [The Billion Laughs Attack](https://en.wikipedia.org/wiki/Billion_laughs_attack)
 
2. Our XPATH implementation is much more complete than both xml.etree
   and even LXML. Additional functions and features are available making
   it easier to quickly parse complex data structures in a single line.

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

